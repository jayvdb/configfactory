import * as ace from 'brace';
import 'brace/mode/json';
import 'brace/theme/twilight';

const editor = ace.edit('id_settings');
editor.setTheme('ace/theme/twilight');
editor.getSession().setMode('ace/mode/json');
editor.setReadOnly(true);
