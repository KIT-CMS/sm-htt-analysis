<?php header('Content-Type: text/html; charset=utf-8'); ?>
<html>
    <head>
        <title><?php echo getcwd(); ?></title>
        <style type='text/css'>
            body{
                font-family: "Candara", sans-serif;
                font-size: 9pt;
                line-height: 10.5pt;
            }
            div.pic{
                display: block;
                float: left;
                background-color: white;
                border: 1px solid #ccc;
                padding: 2px;
                text-align: center;
                margin: 2px 10px 10px 2px;
          }
        </style>
    </head>
    <body>
        <h2><a name="plots"><?php echo getcwd(); ?></a></h2>
        <div>
            <p><form>Filter: <input type="text" name="match" size="30" value="" /><input type="Submit" value="Go" /></form></p>
            <?php
            $remainderFiles = array();
            $remainderFolders = array();
            if ($_GET['noplots']){
                print "Plots will not be displayed.\n";
            }
            else{
                foreach(glob("*") as $filename){
                    if(!preg_match('/.*.(?:png|jpg|jpeg|gif)$/', $filename)){
                        if(is_dir($filename)){
                            array_push($remainderFolders, $filename);
                        }
                        else if(!preg_match('/.*\.php.*$/', $filename)){
                            array_push($remainderFiles, $filename);
                        }
                        continue;
                    }
                    if (isset($_GET['match']) && !preg_match('/'.$_GET['match'].'/', $filename)) continue;
                    print "<div class='pic'>\n";
                    print "<h3><a href=\"$filename\">$filename</a></h3>";
                    print "<a href=\"$filename\"><img src=\"$filename\" style=\"border: none; width: 300px; \"></a>";
                    print "</div>";
                }
            }
            ?>
        </div>
        <div style="display: block; clear:both;">
            <h2><a name="folders">&nbsp;<P>Folders</a></h2>
            <ul>
            <?php
            foreach ($remainderFolders as $filename) {
                print "<li><a href=\"$filename/index.php\">$filename</a></li>";
            }
            ?>
            </ul>
            <h2><a name="files">&nbsp;<P>Files</a></h2>
            <ul>
            <?php
            foreach ($remainderFiles as $filename) {
                print "<li><a href=\"$filename\">$filename</a></li>";
            }
            ?>
            </ul>
        </div>
    </body>
</html>
