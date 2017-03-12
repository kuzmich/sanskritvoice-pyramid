<%inherit file="sv:templates/admin/base.mako"/>

<%block name="head">
    ${parent.head()}

    % for style in resources['css']:
        <link href="${request.static_path(style)}" rel="stylesheet">
    % endfor
</%block>

<%block name="page_header">Новая баджана</%block>

<%block name="body_end">
    ${parent.body_end()}

    % for script in resources['js']:
        <script src="${request.static_path(script)}"></script>
    % endfor
</%block>

${form|n}
