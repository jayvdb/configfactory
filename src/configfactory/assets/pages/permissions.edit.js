import $ from 'jquery';

$('input[name=obj]').change(function () {

    const $this = $(this);
    const objectId = $this.val();
    const perm = $this.data('perm');
    const action = $this.is(':checked') ? 'assign' : 'remove';
    const path = $this.data('path');

    $.post(path, {
        object_id: objectId,
        action: action,
        perm: perm
    }, function (response) {
        if (response.success) {
            if (!perm.startsWith('view_') && action === 'assign') {
                const $view = $this.closest('tr').find('input[data-perm^=view_]');
                if (!$view.is(':checked')) {
                    $view.prop('checked', true);
                    $view.trigger('change');
                }
            }
        }
    })
});
