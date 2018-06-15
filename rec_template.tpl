<table border=1 bgcolor="#00FF7F" width = "85%">
    <tr>
        <th width = "60%">Title</th>
        <th width = "20%">Author</th>
        <th width = "20%">Url</th>
    </tr>
    %for row in rows_g:
        <tr>
            <td><a href="{{row.url}}">{{row.title}}</a></td>
            <td>{{row.author}}</td>
            <td>{{row.url}}</td>
        </tr>
    %end
</table>
<table border=1 bgcolor="#CAFF70" width = "85%">
    %for row in rows_m:
        <tr>
            <td width = "60%"><a href="{{row.url}}">{{row.title}}</a></td>
            <td width = "20%">{{row.author}}</td>
            <td width = "20%">{{row.url}}</td>
        </tr>
    %end
</table>
<table border=1 bgcolor="#CFCFCF" width = "85%">
    %for row in rows_n:
        <tr>
            <td width = "60%"><a href="{{row.url}}">{{row.title}}</a></td>
            <td width = "20%">{{row.author}}</td>
            <td width = "20%">{{row.url}}</td>
        </tr>
    %end
</table>