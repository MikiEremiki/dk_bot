from aiogram_dialog import LaunchMode, Window, Dialog
from aiogram_dialog.widgets.kbd import Start, Cancel

import states
from .custom_widgets.i18n_format import I18NFormat

settings_dialog = Dialog(
    Window(
        I18NFormat('settings-info'),
        Start(
            text=I18NFormat('settings-supply_request'),
            id='settings_supply_request',
            state=states.SupplyRequestSettings.START,
        ),
        Cancel(I18NFormat('cancel')),
        state=states.Settings.MAIN,
    ),
    launch_mode=LaunchMode.ROOT,
)
