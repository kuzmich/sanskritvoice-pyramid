<%block name="head">
    <link rel="stylesheet" href="${request.static_path('sv:static/sm2/bar-ui/css/bar-ui.css')}">
    <style>
        ul.playlist li {
            font-size: 100%;
        }
        ul.playlist li .timing {
            font-size: 60%;
            height: auto;
        }
        ul.playlist li .controls .statusbar {
            height: 0.7em;
        }

        .sm2-bar-ui {
            font-size: 16px;
        }
        .sm2-bar-ui .sm2-main-controls,
        .sm2-bar-ui .sm2-playlist-drawer {
            background-color: #999;
        }
        .sm2-bar-ui .sm2-inline-texture {
            background: #666;
        }
    </style>
</%block>

<%block name="body_start">
<div class="sm2-bar-ui compact full-width flat fixed">

    <div class="bd sm2-main-controls">

        <div class="sm2-inline-texture"></div>
        <div class="sm2-inline-gradient"></div>

        <div class="sm2-inline-element sm2-button-element">
            <div class="sm2-button-bd">
                <a href="#play" class="sm2-inline-button play-pause">Play / pause</a>
            </div>
        </div>

        <div class="sm2-inline-element sm2-inline-status">

            <div class="sm2-playlist">
                <div class="sm2-playlist-target">
                    <!-- playlist <ul> + <li> markup will be injected here -->
                    <!-- if you want default / non-JS content, you can put that here. -->
                    <noscript><p>JavaScript is required.</p></noscript>
                </div>
            </div>

            <div class="sm2-progress">
                <div class="sm2-row">
                    <div class="sm2-inline-time">0:00</div>
                    <div class="sm2-progress-bd">
                        <div class="sm2-progress-track">
                            <div class="sm2-progress-bar"></div>
                            <div class="sm2-progress-ball"><div class="icon-overlay"></div></div>
                        </div>
                    </div>
                    <div class="sm2-inline-duration">0:00</div>
                </div>
            </div>

        </div>

        <div class="sm2-inline-element sm2-button-element sm2-volume">
            <div class="sm2-button-bd">
                <span class="sm2-inline-button sm2-volume-control volume-shade"></span>
                <a href="#volume" class="sm2-inline-button sm2-volume-control">volume</a>
            </div>
        </div>

    </div>

    <div class="bd sm2-playlist-drawer sm2-element">

        <div class="sm2-inline-texture">
            <div class="sm2-box-shadow"></div>
        </div>

        <!-- playlist content is mirrored here -->

        <div class="sm2-playlist-wrapper">
            <ul class="sm2-playlist-bd">
##                 <li><a href="http://freshly-ground.com/data/audio/sm2/Adrian%20Glynn%20-%20Seven%20Or%20Eight%20Days.mp3"><b>Adrian Glynn</b> - Seven Or Eight Days</a></li>
            </ul>
        </div>

    </div>

</div>
</%block>

<%block name="body_end">
    <script src="${request.static_path('sv:static/sm2/script/soundmanager2.js')}"></script>
    <script>
        soundManager.setup({
            url: '${request.static_path("sv:static/sm2/swf/")}',
            html5PollingInterval: 50
            // use soundmanager2-nodebug-jsmin.js, or disable debug mode (enabled by default) after development/testing
            // debugMode: false,
        });
        var PP_CONFIG = {
            playNext: false
        };
        $(document).ready(function() {
            $('p.blog-post-meta a:nth-child(1)').on('click', function(e) {
                var link = $(this);
                var title = link.data('alttext');
                link.data('alttext', link.text());
                link.text(title);

                var p = $(this).parent('p');
                p.nextAll('p.b-text').toggle();
                p.nextAll('p.b-accords').toggle();
                e.preventDefault();
            });
            
            $('ul.playlist a').on('click', function (e) {
                $('ul.sm2-playlist-bd').html('<li></li>');
                $(this).clone().appendTo('ul.sm2-playlist-bd li');

                window.sm2BarPlayers[0].actions.play(this);

                e.preventDefault();
            });
        })
    </script>
    <script src="${request.static_path('sv:static/sm2/bar-ui/script/bar-ui.js')}"></script>
</%block>

