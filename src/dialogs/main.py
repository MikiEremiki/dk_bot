from aiogram_dialog import LaunchMode, Window, Dialog
from aiogram_dialog.widgets.kbd import Start, Cancel
from aiogram_dialog.widgets.text import Const

import states
from .custom_widgets.i18n_format import I18NFormat

main_dialog = Dialog(
    Window(
        #TODO Вынести текст из const в ftl и прописать тексты
        Const('This is aiogram-dialog demo application'),
        Const('Use buttons below to see some options.'),
        Start(
            text=I18NFormat('supply_request-create'),
            id='supply_request_create',
            state=states.SupplyRequest.START,
        ),
        Start(
            text=I18NFormat('register-start'),
            id='register_start',
            state=states.Register.PHONE,
        ),
        Cancel(I18NFormat('cancel')),
        state=states.Main.MAIN,
    ),
    launch_mode=LaunchMode.ROOT,
)
