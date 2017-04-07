##<%inherit file="sv:templates/bootstrap_base.mako"/>
<%inherit file="../bootstrap_base.mako"/>
<%namespace name="player" file="../players/sm2.mako"/>

<%block name="title">Голос санскрита</%block>

<%block name="head">
    <link href="${request.static_path('sv:static/css/blog.css')}" rel="stylesheet">
    ${player.head()}
</%block>

<%block name="body_start">${player.body_start()}</%block>
<%block name="body_end">
    ${parent.body_end()}
    ${player.body_end()}
</%block>

##<%block name="body">
    <nav class="navbar navbar-default">
      <div class="container-fluid">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#categories" aria-expanded="false">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="/">Голос санскрита</a>
        </div>
        <div class="collapse navbar-collapse" id="categories">
          <ul class="nav navbar-nav">
            % for c in categories:
              <%
                path = request.route_path('category', category=c[0])
                active = (path == request.path)
              %>
              <li ${'class=active' if active else ''}>
                <a href="${path}">${c[1]}
                  % if active:
                    <span class="sr-only">(current)</span>
                  % endif
                </a>
              </li>
            % endfor
            <li><a href="/about">О сайте</a></li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container">
      <div class="row">
        <div class="col-md-8 blog-main">
          ${next.body()}
        </div><!-- /.blog-main -->
      </div><!-- /.row -->
    </div><!-- /.container -->

<%doc>
    <footer class="blog-footer">
      <p><a href="https://github.com/kuzmich/sanskritvoice">Исходный код</a></p>
    </footer>
</%doc>
##</%block>
