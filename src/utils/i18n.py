from fluent_compiler.bundle import FluentBundle

from fluentogram import FluentTranslator, TranslatorHub

from config.config import Config


def create_translator_hub(config: Config) -> TranslatorHub:
    translator_hub = TranslatorHub(
        {
            'ru': 'ru',
        },
        [
            FluentTranslator(
                locale='ru',
                translator=FluentBundle.from_files(
                    locale='ru-RU',
                    filenames=[config.paths.locales]),
                separator='-'
            ),
        ],
        root_locale='ru'
    )
    return translator_hub
