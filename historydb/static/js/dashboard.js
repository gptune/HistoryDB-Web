// Author: Younghyun Cho <younghyun@berkeley.edu>

function UpdateDeps(machine_deps_avail, software_deps_avail, users_avail, search_data_avail) {
    var application_var = document.getElementById("applicationVal");
    var application_name = application_var.options[application_var.selectedIndex].value;

    document.getElementById('select_deps').innerHTML = "<b>Select available tuning configurations (click each option to see the details)</b>";

    var machine_deps_div = document.getElementById("machine_deps");
    machine_deps_div.innerHTML = "Machine configurations";
    for (i=0; i<machine_deps_avail[application_name].length; i++) {
        var x = document.createElement('div');
        x.classList.add('panel_group');
        x.classList.add('custom-control');
        x.classList.add('custom-checkbox');

        var x1 = document.createElement('input');
        x1.type = 'checkbox';
        x1.classList.add('custom-control-input');
        x1.setAttribute('id', 'machine_deps_option'+i);
        x1.setAttribute('value', JSON.stringify(machine_deps_avail[application_name][i], null, 2));
        x1.setAttribute('name', 'machine_deps_list');

        var x2 = document.createElement('label');
        x2.classList.add('custom-control-label');
        x2.htmlFor = x1.id;

        var x2_1 = document.createElement('div');
        x2_1.classList.add('panel');
        x2_1.classList.add('panel-default');
        x2_1.innerHTML = "<a data-toggle='collapse' href='#machine_deps_option"+i+"_detail'>Option " + (i+1) + " (" + machine_deps_avail[application_name][i]["machine"] + ")</a>";

        var x2_1_1 = document.createElement('div');
        x2_1_1.id = 'machine_deps_option'+i+'_detail'
        x2_1_1.classList.add('panel-collapse');
        x2_1_1.classList.add('collapse');
        x2_1_1.innerHTML = "<pre>"+JSON.stringify(machine_deps_avail[application_name][i], null, 2)+"</pre>";

        x2_1.appendChild(x2_1_1);
        x2.appendChild(x2_1);

        x.innerHTML = "";
        x.appendChild(x1);
        x.appendChild(x2);

        machine_deps_div.appendChild(x);
    }

    var software_deps_div = document.getElementById("software_deps");
    software_deps_div.innerHTML = "Software configurations";
    for (i=0; i<software_deps_avail[application_name].length; i++) {
        var x = document.createElement('div');
        x.classList.add('panel_group');
        x.classList.add('custom-control');
        x.classList.add('custom-checkbox');

        var x1 = document.createElement('input');
        x1.type = 'checkbox';
        x1.classList.add('custom-control-input');
        x1.setAttribute('id', 'software_deps_option'+i);
        x1.setAttribute('value', JSON.stringify(software_deps_avail[application_name][i], null, 2));
        x1.setAttribute('name', 'software_deps_list');

        var x2 = document.createElement('label');
        x2.classList.add('custom-control-label');
        x2.htmlFor = x1.id;

        var x2_1 = document.createElement('div');
        x2_1.classList.add('panel');
        x2_1.classList.add('panel-default');
        x2_1.innerHTML = "<a data-toggle='collapse' href='#software_deps_option"+i+"_detail'>Option " + (i+1) + "</a>";

        var x2_1_1 = document.createElement('div');
        x2_1_1.id = 'software_deps_option'+i+'_detail'
        x2_1_1.classList.add('panel-collapse');
        x2_1_1.classList.add('collapse');
        x2_1_1.innerHTML = "<pre>"+JSON.stringify(software_deps_avail[application_name][i], null, 2)+"</pre>";

        x2_1.appendChild(x2_1_1);
        x2.appendChild(x2_1);

        x.innerHTML = "";
        x.appendChild(x1);
        x.appendChild(x2);

        software_deps_div.appendChild(x);
    }

    var user_deps_div = document.getElementById("user_deps");
    user_deps_div.innerHTML = "User list";
    for (i=0; i<users_avail[application_name].length; i++) {
        var x = document.createElement('div');
        x.classList.add('panel_group');
        x.classList.add('custom-control');
        x.classList.add('custom-checkbox');

        var x1 = document.createElement('input');
        x1.type = 'checkbox';
        x1.classList.add('custom-control-input');
        x1.setAttribute('id', 'user_deps_option'+i);
        x1.setAttribute('value', JSON.stringify(users_avail[application_name][i], null, 2));
        x1.setAttribute('name', 'users_list');

        var x2 = document.createElement('label');
        x2.classList.add('custom-control-label');
        x2.htmlFor = x1.id;

        var x2_1 = document.createElement('div');
        x2_1.classList.add('panel');
        x2_1.classList.add('panel-default');
        x2_1.innerHTML = "<a data-toggle='collapse' href='#user_deps_option"+i+"_detail'>Option " + (i+1) + " (" + users_avail[application_name][i]["name"] + ")</a>";

        var x2_1_1 = document.createElement('div');
        x2_1_1.id = 'user_deps_option'+i+'_detail'
        x2_1_1.classList.add('panel-collapse');
        x2_1_1.classList.add('collapse');
        x2_1_1.innerHTML = "<pre>"+JSON.stringify(users_avail[application_name][i], null, 2)+"</pre>";

        x2_1.appendChild(x2_1_1);
        x2.appendChild(x2_1);

        x.innerHTML = "";
        x.appendChild(x1);
        x.appendChild(x2);

        user_deps_div.appendChild(x);
    }

    var search_data_div = document.getElementById("search_data");
    search_data_div.innerHTML = "Search data";
    {
        var x = document.createElement('div');
        x.classList.add('panel_group');
        x.classList.add('custom-control');
        x.classList.add('custom-checkbox');
        x.innerHTML = "";
        var x1 = document.createElement("input");
        x1.type = 'checkbox';
        x1.classList.add('custom-control-input');
        x1.setAttribute("value", "func_eval");
        x1.setAttribute("name", "search_data");
        x1.setAttribute("id", "search_data_func_eval");
        x.appendChild(x1);
        var label1 = document.createElement("label");
        label1.classList.add('custom-control-label');
        label1.innerHTML = 'func_eval';
        label1.htmlFor = x1.id;
        x.appendChild(label1);
        search_data_div.appendChild(x);
    }
    {
        var x = document.createElement('div');
        x.classList.add('panel_group');
        x.classList.add('custom-control');
        x.classList.add('custom-checkbox');
        x.innerHTML = "";
        var x1 = document.createElement("input");
        x1.type = 'checkbox';
        x1.classList.add('custom-control-input');
        x1.setAttribute("value", "model_data");
        x1.setAttribute("name", "search_data");
        x1.setAttribute("id", "search_data_model_data");
        x.appendChild(x1);
        var label1 = document.createElement("label");
        label1.classList.add('custom-control-label');
        label1.innerHTML = 'model_data';
        label1.htmlFor = x1.id;
        x.appendChild(label1);
        search_data_div.appendChild(x);
    }
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

