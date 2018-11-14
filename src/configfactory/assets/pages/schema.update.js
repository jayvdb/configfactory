import $ from 'jquery';
import * as ace from 'brace';
import 'brace/mode/json';
import 'brace/theme/twilight';

const $schema = $('#id_schema');
const editor = ace.edit('json-editor');
editor.$blockScrolling = Infinity;
editor.setTheme('ace/theme/twilight');
editor.getSession().setMode('ace/mode/json');
editor.getSession().setValue($schema.val());
editor.getSession().on('change', function () {
    $schema.val(editor.getSession().getValue());
});