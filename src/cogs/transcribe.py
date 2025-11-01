import io
import json
import typing
import os

import discord
from discord import app_commands
from discord.ext import commands
import pydub
import speech_recognition as sr
import deepl


class Transcriber(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()
        self.deepl_api_key = os.getenv("DEEPL_API_KEY")
        self.max_duration = int(os.getenv("MAX_VOICE_MESSAGE_DURATION", "60"))

        deepl_free_api = os.getenv("DEEPL_FREE_API", "false").lower() == "true"
        self.deepl_server_url = "https://api-free.deepl.com" if deepl_free_api else None

        self.selected_messages = {}

        self.select_menu = app_commands.ContextMenu(
            name="Select Voice Message",
            callback=self.select_voice_message,
        )
        self.select_menu.allowed_installs = app_commands.AppInstallationType(
            guild=True, user=True
        )
        self.select_menu.allowed_contexts = app_commands.AppCommandContext(
            guild=True, dm_channel=True, private_channel=True
        )
        self.bot.tree.add_command(self.select_menu)

    async def cog_unload(self):
        self.bot.tree.remove_command(self.select_menu.name, type=self.select_menu.type)

    def load_config(self):
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "config", "config.json"
        )
        with open(config_path) as conf_file:
            return json.load(conf_file)

    async def select_voice_message(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        if not message.attachments or not (message.flags.value & (1 << 13)):
            await interaction.response.send_message(
                "This message does not contain a voice message.", ephemeral=True
            )
            return

        attachment = message.attachments[0]
        duration = getattr(attachment, "duration_secs", None)
        if duration and duration > self.max_duration:
            await interaction.response.send_message(
                f"Voice message is too long. Maximum duration is {self.max_duration} seconds. This voice message is {int(duration)} seconds.",
                ephemeral=True,
            )
            return

        self.selected_messages[interaction.user.id] = message
        await interaction.response.send_message(
            f"Voice message selected! Use /transcribe to transcribe it.", ephemeral=True
        )

    async def language_autocomplete(
        self, interaction: discord.Interaction, current: str
    ):
        language_codes = self.config["language_codes"]

        popular_languages = [
            "EN-US",
            "ES",
            "FR",
            "DE",
            "JA",
            "ZH",
            "PT-BR",
            "RU",
            "IT",
            "NL",
        ]

        if not current:
            choices = [
                app_commands.Choice(name=f"{code} - {language_codes[code]}", value=code)
                for code in popular_languages
                if code in language_codes
            ]
            return choices[:25]

        current_upper = current.upper()
        current_lower = current.lower()

        exact_matches = []
        code_matches = []
        name_matches = []

        for code, name in language_codes.items():
            if code == current_upper:
                exact_matches.append((code, name))
            elif code.startswith(current_upper):
                code_matches.append((code, name))
            elif current_lower in name.lower():
                name_matches.append((code, name))

        all_matches = exact_matches + code_matches + name_matches
        choices = [
            app_commands.Choice(name=f"{code} - {name}", value=code)
            for code, name in all_matches
        ]

        return choices[:25]

    @app_commands.command(
        name="transcribe", description="Transcribe the selected voice message"
    )
    @app_commands.describe(
        translate_to="Language code to translate to (e.g., EN-US, ES, FR)",
        public="Should everyone see this response? (default: false)",
    )
    @app_commands.autocomplete(translate_to=language_autocomplete)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def transcribe(
        self,
        interaction: discord.Interaction,
        translate_to: str = None,
        public: bool = False,
    ):
        if interaction.user.id not in self.selected_messages:
            await interaction.response.send_message(
                "No voice message selected! Right-click a message and select 'Select Voice Message' first.",
                ephemeral=True,
            )
            return

        message = self.selected_messages[interaction.user.id]
        await self._transcribe_message(interaction, message, translate_to, public)

    async def _transcribe_message(
        self,
        interaction: discord.Interaction,
        message: discord.Message,
        translate_to: str = None,
        public: bool = False,
    ):
        await interaction.response.defer(ephemeral=not public)

        if translate_to is not None:
            translate_to = translate_to.upper()
            language_codes = self.config["language_codes"]
            if translate_to not in language_codes:
                valid_codes = ", ".join([f"`{code}`" for code in language_codes])
                await interaction.followup.send(
                    f"**Invalid language code.**\n> Valid language codes: {valid_codes}",
                    ephemeral=True,
                )
                return

        if not msg_has_voice_note(message):
            await interaction.followup.send(
                "This message does not contain a voice message.", ephemeral=True
            )
            return

        author = message.author

        try:
            transcribed_text = await transcribe_msg(message)

            translated_text = None
            if translate_to is not None and transcribed_text:
                try:
                    if self.deepl_server_url:
                        deepl_translator = deepl.Translator(
                            auth_key=self.deepl_api_key,
                            server_url=self.deepl_server_url,
                        )
                    else:
                        deepl_translator = deepl.Translator(auth_key=self.deepl_api_key)

                    result = deepl_translator.translate_text(
                        transcribed_text, target_lang=translate_to
                    )
                    translated_text = (
                        result.text if hasattr(result, "text") else str(result)
                    )
                except Exception as translation_error:
                    print(f"Translation error: {translation_error}")
                    translated_text = None

            embed = make_embed(
                transcribed_text,
                author,
                interaction.user,
                translate_to,
                translated_text,
            )

            await interaction.followup.send(embed=embed, ephemeral=not public)

        except sr.UnknownValueError as e:
            await interaction.followup.send(
                f"Could not transcribe the Voice Message from {author} as the response was empty.",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                f"Could not transcribe the Voice Message from {author} due to an error.",
                ephemeral=True,
            )
            print(e)


def make_embed(
    transcribed_text, author, ctx_author=None, translate_to=None, translated_text=None
):
    embed = discord.Embed(
        color=0xACD8AA,
        title=f"{author.name}'s Voice Message",
    )
    embed.add_field(
        name=f"Transcription",
        value=transcribed_text,
        inline=False,
    )

    if translate_to and translated_text:
        embed.add_field(
            name=f"Translation (Into {translate_to.upper()})",
            value=str(translated_text),
            inline=False,
        )

    if ctx_author:
        embed.set_footer(text=f"Requested by {ctx_author.name}")

    return embed


def msg_has_voice_note(msg: typing.Optional[discord.Message]) -> bool:
    if not msg:
        return False
    if not msg.attachments or not msg.flags.value >> 13:
        return False
    return True


async def transcribe_msg(
    msg: typing.Optional[discord.Message],
) -> typing.Optional[typing.Union[typing.Any, list, tuple]]:
    if not msg or not msg_has_voice_note(msg):
        return None

    voice_msg_bytes = await msg.attachments[0].read()
    voice_msg = io.BytesIO(voice_msg_bytes)

    audio_segment = pydub.AudioSegment.from_file(voice_msg)
    wav_bytes = io.BytesIO()
    audio_segment.export(wav_bytes, format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_bytes) as source:
        audio_data = recognizer.record(source)

    try:
        transcribed_text = recognizer.recognize_google(audio_data)

    except sr.UnknownValueError as e:
        raise e

    except Exception as e:
        raise e

    return transcribed_text


async def setup(bot):
    await bot.add_cog(Transcriber(bot))
