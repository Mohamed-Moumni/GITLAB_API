/** @odoo-module **/

import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";

import { user_menu_items } from "@web/webclient/user_menu/user_menu_items"; // eslint-disable-line no-unused-vars

function kzmAssistanceItem(env) {
    return {
        type: "item",
        id: "assistance",
        description: env._t("Karizma Assistance"),
        callback: () => {
            browser.location.href = "https://erp.karizma.cc/openticket";
        },
        sequence: 20,
    }
}

registry.category("user_menuitems").remove("support");
registry.category("user_menuitems").remove("odoo_account");
registry.category("user_menuitems").add("assistance", kzmAssistanceItem);