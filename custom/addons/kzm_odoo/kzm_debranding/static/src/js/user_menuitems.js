/** @odoo-module **/

import {registry} from "@web/core/registry";
import {user_menu_items} from "@web/webclient/user_menu/user_menu_items"; // eslint-disable-line no-unused-vars

registry.category("user_menuitems").remove("support");
registry.category("user_menuitems").remove("odoo_account");