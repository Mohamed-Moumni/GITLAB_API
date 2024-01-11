odoo.define('kzm_support.website_support', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');

    var _t = core._t;

    $(function() {
      $("#addMore").click(function(e) {
      var i=0;
        $('#fieldList').find('input').each(function(){
            var temp='File'+i;
            $(this).attr('name',temp);
            ++i;
        });
        $("#fieldList").append("<div class='form-group form-field o_website_form_custom'><div class='col-md-3 col-sm-4 text-right'></div><div class='col-md-7 col-sm-8'><input type='file' class='form-control o_website_form_input' name='File2'/></div>");
      });
    });

});
