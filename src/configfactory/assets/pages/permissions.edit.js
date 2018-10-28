import $ from 'jquery';

$('input[name=obj]').change(function () {

    const ACTION_ASSIGN = 'assign';
    const ACTION_REMOVE = 'remove';
    const $this = $(this);
    const objectId = $this.val();
    const perm = $this.data('perm');
    const action = $this.is(':checked') ? ACTION_ASSIGN : ACTION_REMOVE;
    const path = $this.data('path');

    $.post(path, {
        object_id: objectId,
        action: action,
        perm: perm
    }, function (response) {
        if (response.success) {
            if (!perm.startsWith('view_') && action === ACTION_ASSIGN) {
                const $view = $this.closest('tr').find('input[data-perm^=view_]');
                if (!$view.is(':checked')) {
                    $view.prop('checked', true);
                    $view.trigger('change');
                }
            }
        }
    })
});
