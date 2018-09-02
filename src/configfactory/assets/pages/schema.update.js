import * as ace from 'brace';
import 'brace/mode/json';
import 'brace/theme/twilight';

const editor = ace.edit('id_schema');
editor.setTheme('ace/theme/twilight');
editor.getSession().setMode('ace/mode/json');
