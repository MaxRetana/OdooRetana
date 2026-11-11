/** @odoo-module **/

import { reactive, useState } from "@odoo/owl";
import { Chatter } from "@mail/chatter/web_portal/chatter";
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { FormRenderer } from "@web/views/form/form_renderer";

const STORAGE_KEY = "retana_bills.chatter_position";
// Modelos cuyo chatter muestra el botón para cambiar de posición.
const MODELS_WITH_TOGGLE = ["retana.budget"];

function readStoredPosition() {
    try {
        return window.localStorage.getItem(STORAGE_KEY) === "bottom" ? "bottom" : "side";
    } catch {
        return "side";
    }
}

// Estado compartido entre el chatter, el controlador y el renderer del formulario.
export const chatterPosition = reactive({ value: readStoredPosition() });

function setPosition(value) {
    chatterPosition.value = value;
    try {
        window.localStorage.setItem(STORAGE_KEY, value);
    } catch {
        // sin almacenamiento disponible: la preferencia solo dura la sesión
    }
}

function isBottomFor(resModel, state) {
    return MODELS_WITH_TOGGLE.includes(resModel) && state.value === "bottom";
}

// Botón dentro del chatter.
patch(Chatter.prototype, {
    setup() {
        super.setup();
        this.retanaChatterPosition = useState(chatterPosition);
    },
    get showRetanaPositionToggle() {
        return MODELS_WITH_TOGGLE.includes(this.props.threadModel);
    },
    get isRetanaChatterBottom() {
        return this.retanaChatterPosition.value === "bottom";
    },
    toggleRetanaChatterPosition() {
        setPosition(this.isRetanaChatterBottom ? "side" : "bottom");
    },
});

// Odoo fuerza el diseño en dos columnas con la clase o_xxl_form_view en pantallas
// muy anchas; se quita cuando el usuario eligió el chatter abajo.
patch(FormController.prototype, {
    setup() {
        super.setup();
        this.retanaChatterPosition = useState(chatterPosition);
    },
    get className() {
        const result = super.className;
        if (isBottomFor(this.props.resModel, this.retanaChatterPosition)) {
            delete result["o_xxl_form_view h-100"];
        }
        return result;
    },
});

// El layout lateral pasa a ser inferior.
patch(FormRenderer.prototype, {
    setup() {
        super.setup();
        this.retanaChatterPosition = useState(chatterPosition);
    },
    mailLayout(hasAttachmentContainer) {
        const layout = super.mailLayout(hasAttachmentContainer);
        if (
            layout === "SIDE_CHATTER" &&
            isBottomFor(this.props.record.resModel, this.retanaChatterPosition)
        ) {
            return "BOTTOM_CHATTER";
        }
        return layout;
    },
});
