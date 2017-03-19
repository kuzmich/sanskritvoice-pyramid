<%inherit file="sv:templates/admin/base.mako"/>

<%block name="head">
    ${parent.head()}

    % for style in resources['css']:
        <link href="${request.static_path(style)}" rel="stylesheet">
    % endfor

    % for script in resources['js']:
        <script src="${request.static_path(script)}"></script>
    % endfor
</%block>

<%block name="page_header">${bhajan.title}</%block>

${form|n}

