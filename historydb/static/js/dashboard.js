// Author: Younghyun Cho <younghyun@berkeley.edu>

function UpdateDeps(machine_deps_avail, software_deps_avail, users_avail) {
    var application_var = document.getElementById("applicationVal");
    var application_name = application_var.options[application_var.selectedIndex].value;

    var machine_deps_div = document.getElementById("machine_deps");
    machine_deps_div.innerHTML = "<b>Available Machine Configurations</b><br><br>";
    for (i=0; i<machine_deps_avail[application_name].length; i++) {
        var x = document.createElement("input");
        x.setAttribute("type", "checkbox");
        x.setAttribute("value", JSON.stringify(machine_deps_avail[application_name][i], null, 2));
        x.setAttribute("name", "machine_deps_list");
        machine_deps_div.appendChild(x);

        var label = document.createElement("label");
        label.innerHTML = "&nbsp; Option " + (i+1) + " (" + machine_deps_avail[application_name][i]["machine"] + ")";
        machine_deps_div.appendChild(label);
        var label2 = document.createElement("label");
        label2.innerHTML = "<details> <summary>JSON details</summary><p><pre>" + JSON.stringify(machine_deps_avail[application_name][i], null, 2) + "</pre></p></details>";
        machine_deps_div.appendChild(label2);

        var linebreak = document.createElement("br");
        linebreak.appendChild(document.createTextNode(machine_deps_avail[application_name][i]));
        machine_deps_div.appendChild(linebreak);
    }

    var software_deps_div = document.getElementById("software_deps");
    software_deps_div.innerHTML = "<b>Available Software Configurations</b><br><br>";
    for (i=0; i<software_deps_avail[application_name].length; i++) {
        var x = document.createElement("input");
        x.setAttribute("type", "checkbox");
        x.setAttribute("value", JSON.stringify(software_deps_avail[application_name][i], null, 2));
        x.setAttribute("name", "software_deps_list")
        software_deps_div.appendChild(x);

        var label = document.createElement("label");
        label.innerHTML = "&nbsp; Option " + (i+1) + "&nbsp;&nbsp;<br>";
        software_deps_div.appendChild(label);
        var label2 = document.createElement("label");
        label2.innerHTML = "<details> <summary>JSON details</summary><p><pre>" + JSON.stringify(software_deps_avail[application_name][i], null, 2) + "</pre></p></details>";
        software_deps_div.appendChild(label2);

        var linebreak = document.createElement("br");
        linebreak.appendChild(document.createTextNode(software_deps_avail[application_name][i]));
        software_deps_div.appendChild(linebreak);
    }

    var users_div = document.getElementById("users_deps");
    users_div.innerHTML = "<b>Available User List</b><br><br>";
    for (i=0; i<users_avail[application_name].length; i++) {
        var x = document.createElement("input");
        x.setAttribute("type", "checkbox");
        x.setAttribute("value", JSON.stringify(users_avail[application_name][i], null, 2));
        x.setAttribute("name", "users_list");
        users_div.appendChild(x);

        var label = document.createElement("label");
        label.innerHTML = "&nbsp; Option " + (i+1) + " (" + users_avail[application_name][i]["name"] + ")";
        users_div.appendChild(label);
        var label2 = document.createElement("label");
        label2.innerHTML = "<details> <summary>JSON details</summary><p><pre>" + JSON.stringify(users_avail[application_name][i], null, 2) + "</pre></p></details>";
        users_div.appendChild(label2);

        var linebreak = document.createElement("br");
        linebreak.appendChild(document.createTextNode(users_avail[application_name][i]));
        users_div.appendChild(linebreak);
    }

    var search_data_div = document.getElementById("search_data");
    search_data_div.innerHTML = "<b>Search Data</b><br><br>";
    var x1 = document.createElement("input");
    x1.setAttribute("type", "checkbox");
    x1.setAttribute("value", "func_eval");
    x1.setAttribute("name", "search_data");
    search_data_div.appendChild(x1);
    var label1 = document.createElement("label");
    label1.innerHTML = "&nbsp; func_eval";
    search_data_div.appendChild(label1);
    var linebreak1 = document.createElement("br");
    linebreak1.appendChild(document.createTextNode("func_eval"));
    search_data_div.appendChild(linebreak1);

    var x2 = document.createElement("input");
    x2.setAttribute("type", "checkbox");
    x2.setAttribute("value", "model_data");
    x2.setAttribute("name", "search_data");
    search_data_div.appendChild(x2);
    var label2 = document.createElement("label");
    label2.innerHTML = "&nbsp; model_data";
    search_data_div.appendChild(label2);
    var linebreak2 = document.createElement("br");
    linebreak2.appendChild(document.createTextNode("model_data"));
    search_data_div.appendChild(linebreak2);
}

function UpdateCond(application_info, machine_deps_list, software_deps_list, users_list) {
    var application_cond_div = document.getElementById("application_cond");
    var application_label = document.createElement("label");
    application_label.innerHTML = "<b>Application selected</b><br><br>";
    application_cond_div.appendChild(application_label);
    var label1 = document.createElement("label");
    label1.innerHTML = "<details><summary>JSON details</summary><p><pre>" + JSON.stringify(application_info, null, 2) + "</pre></p></details>";
    application_cond_div.appendChild(label1);

    var machine_deps_cond_div = document.getElementById("machine_deps_cond");
    var machine_deps_label = document.createElement("label");
    machine_deps_label.innerHTML = "<b>Machine configuration selected</b><br><br>";
    machine_deps_cond_div.appendChild(machine_deps_label);
    var label2 = document.createElement("label");
    label2.innerHTML = "<details><summary>JSON details</summary><p><pre>" + JSON.stringify(machine_deps_list, null, 2) + "</pre></p></details>";
    machine_deps_cond_div.appendChild(label2);

    var software_deps_cond_div = document.getElementById("software_deps_cond");
    var software_deps_label = document.createElement("label");
    software_deps_label.innerHTML = "<b>Software configuration selected</b><br><br>";
    software_deps_cond_div.appendChild(software_deps_label);
    var label3 = document.createElement("label");
    label3.innerHTML = "<details><summary>JSON details</summary><p><pre>" + JSON.stringify(software_deps_list, null, 2) + "</pre></p></details>";
    software_deps_cond_div.appendChild(label3);

    var users_cond_div = document.getElementById("users_cond");
    var users_label = document.createElement("label");
    users_label.innerHTML = "<b>Software configuration selected</b><br><br>";
    users_cond_div.appendChild(users_label);
    var label4 = document.createElement("label");
    label4.innerHTML = "<details><summary>JSON details</summary><p><pre>" + JSON.stringify(users_list, null, 2) + "</pre></p></details>";
    users_cond_div.appendChild(label4);
}

