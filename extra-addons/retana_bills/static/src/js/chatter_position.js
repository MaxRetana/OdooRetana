/** @odoo-module **/

import { Component, reactive, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";

const STORAGE_KEY = "retana_bills.chatter_position";

function readStoredPosition() {
    try {
        return window.localStorage.getItem(STORAGE_KEY) === "bottom" ? "bottom" : "side";
    } catch {
        return "side";
    }
}

// Estado compartido entre el botón y el renderer del formulario.
export const chatterPosition = reactive({ value: readStoredPosition() });

function setPosition(value) {
    chatterPosition.value = value;
    try {
        window.localStorage.setItem(STORAGE_KEY, value);
    } catch {
        // sin almacenamiento disponible: la preferencia solo dura la sesión
    }
}

export class ChatterPositionToggle extends Component {
    static template = "retana_bills.ChatterPositionToggle";
    static props = { ...standardWidgetProps };

    setup() {
        this.state = useState(chatterPosition);
    }

    get isBottom() {
        return this.state.value === "bottom";
    }

    toggle() {
        setPosition(this.isBottom ? "side" : "bottom");
    }
}

registry.category("view_widgets").add("retana_chatter_position_toggle", {
    component: ChatterPositionToggle,
});

// Si el usuario eligió el chatter abajo, el layout lateral pasa a ser inferior.
patch(FormRenderer.prototype, {
    setup() {
        super.setup();
        this.retanaChatterPosition = useState(chatterPosition);
    },
    mailLayout(hasAttachmentContainer) {
        const layout = super.mailLayout(hasAttachmentContainer);
        if (this.retanaChatterPosition.value === "bottom" && layout === "SIDE_CHATTER") {
            return "BOTTOM_CHATTER";
        }
        return layout;
    },
});
