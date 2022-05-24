<?php
    header('Content-Type: text/html; charset=utf-8');
   
    $zip = new ZipArchive;
    $filename = 'parser_ulpressa.zip';
    if($zip -> open(__DIR__.'/'.$filename)){

        $zip->extractTo(__DIR__);

        echo 'Файлы разархивированы удачно!';
    }
    else{
        echo 'Не удачная попытка разархивации!';
    }
?>