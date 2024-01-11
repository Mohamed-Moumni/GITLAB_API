/** @odoo-module */

import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useService } from "@web/core/utils/hooks";
import { browser } from "@web/core/browser/browser";
import { download } from "@web/core/network/download";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { FileInput } from "@web/core/file_input/file_input";

import { Component } from "@odoo/owl";

export class HomeMenuCustomizer extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.ui = useService("ui");
        this.notification = useService("notification");
        this.company = useService("company");
        this.user = useService("user");
        this.actionManager = useService("action");
        this.menus = useService("menu");
        this.dialogManager = useService("dialog");
    }

    setBackgroundImage(attachment_id) {
        return this.rpc("/web_studio/set_background_image", {
            attachment_id: attachment_id,
            context: this.user.context,
        });
    }







}
HomeMenuCustomizer.template = "kzm_debranding.HomeMenuCustomizer";
HomeMenuCustomizer.components = { Dropdown, DropdownItem, FileInput };
