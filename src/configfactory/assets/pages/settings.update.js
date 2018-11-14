import $ from 'jquery';
import * as ace from 'brace';
import 'brace/mode/json';
import 'brace/theme/twilight';

const $settings = $('#id_settings');
const editor = ace.edit('json-editor');
editor.$blockScrolling = Infinity;
editor.setTheme('ace/theme/twilight');
editor.getSession().setMode('ace/mode/json');
editor.getSession().setValue($settings.val());
editor.getSession().on('change', function () {
    $settings.val(editor.getSession().getValue());
});