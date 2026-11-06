/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class AmountSelectorField extends Component {
    static template = "retana_bills.AmountSelectorField";
    static props = {
        ...standardFieldProps,
    };
    
    static supportedTypes = ["float", "integer", "monetary"];

    setup() {
        this.state = useState({
            showCustomInput: false,
            customValue: "",
        });
        
        // Generar los montos para el grid 3x3 (de 1000 a 9000)
        this.amounts = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000];
    }

    /**
     * Establece el monto seleccionado en el campo
     */
    setAmount(amount) {
        this.props.record.update({ [this.props.name]: amount });
        this.state.showCustomInput = false;
        this.state.customValue = "";
    }

    /**
     * Muestra el input para cantidad personalizada
     */
    showCustomAmount() {
        this.state.showCustomInput = true;
        this.state.customValue = this.props.record.data[this.props.name] || "";
    }

    /**
     * Cancela la entrada personalizada
     */
    cancelCustom() {
        this.state.showCustomInput = false;
        this.state.customValue = "";
    }

    /**
     * Confirma el monto personalizado
     */
    confirmCustomAmount() {
        const amount = parseFloat(this.state.customValue) || 0;
        if (amount > 0) {
            this.setAmount(amount);
        }
    }

    /**
     * Formatea el monto con separadores de miles
     */
    formatAmount(amount) {
        return new Intl.NumberFormat('es-MX', {
            style: 'currency',
            currency: 'MXN',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(amount);
    }

    /**
     * Obtiene el valor actual del campo
     */
    get currentValue() {
        return this.props.record.data[this.props.name] || 0;
    }
}

registry.category("fields").add("retana_bills.amount_selector", {
    component: AmountSelectorField,
    supportedTypes: ["float", "integer", "monetary"],
});
