// Author: Younghyun Cho <younghyun@berkeley.edu>

function UpdateConfigurationsList(machine_configurations_avail, software_configurations_avail, user_configurations_avail) {
    var tuning_problem_unique_name = document.getElementById('tuning_problem_id').options[document.getElementById('tuning_problem_id').selectedIndex].value;

    document.getElementById('select_configurations').innerHTML = "<b>Select available tuning configurations (click each option to see the details)</b>";

    var machine_configurations_div = document.getElementById("machine_configurations");
    machine_configurations_div.innerHTML = "Machine configurations";
    for (i=0; i<machine_configurations_avail[tuning_problem_unique_name].length; i++) {
        var x = document.createElement('div');
        x.classList.add('panel_group');
        x.classList.add('custom-control');
        x.classList.add('custom-checkbox');

        var x1 = document.createElement('input');
        x1.type = 'checkbox';
        x1.classList.add('custom-control-input');
        x1.setAttribute('id', 'machine_configurations_option'+i);
        x1.setAttribute('value', JSON.stringify(machine_configurations_avail[tuning_problem_unique_name][i], null, 2));
        x1.setAttribute('name', 'machine_configurations_list');
        x1.setAttribute('checked', true);

        var x2 = document.createElement('label');
        x2.classList.add('custom-control-label');
        x2.htmlFor = x1.id;

        var x2_1 = document.createElement('div');
        x2_1.classList.add('panel');
        x2_1.classList.add('panel-default');
        x2_1.innerHTML = "<a data-toggle='collapse' href='#machine_configurations_option"+i+"_detail'>Option " + (i+1) + " (" + machine_configurations_avail[tuning_problem_unique_name][i]["machine_name"] + ")</a>";

        var x2_1_1 = document.createElement('div');
        x2_1_1.id = 'machine_configurations_option'+i+'_detail'
        x2_1_1.classList.add('panel-collapse');
        x2_1_1.classList.add('collapse');
        x2_1_1.innerHTML = "<pre>"+JSON.stringify(machine_configurations_avail[tuning_problem_unique_name][i], null, 2)+"</pre>";

        x2_1.appendChild(x2_1_1);
        x2.appendChild(x2_1);

        x.innerHTML = "";
        x.appendChild(x1);
        x.appendChild(x2);

        machine_configurations_div.appendChild(x);
    }

    var software_configurations_div = document.getElementById("software_configurations");
    software_configurations_div.innerHTML = "Software configurations";
    for (i=0; i<software_configurations_avail[tuning_problem_unique_name].length; i++) {
        var x = document.createElement('div');
        x.classList.add('panel_group');
        x.classList.add('custom-control');
        x.classList.add('custom-checkbox');

        var x1 = document.createElement('input');
        x1.type = 'checkbox';
        x1.classList.add('custom-control-input');
        x1.setAttribute('id', 'software_configurations_option'+i);
        x1.setAttribute('value', JSON.stringify(software_configurations_avail[tuning_problem_unique_name][i], null, 2));
        x1.setAttribute('name', 'software_configurations_list');
        x1.setAttribute('checked', true);

        var x2 = document.createElement('label');
        x2.classList.add('custom-control-label');
        x2.htmlFor = x1.id;

        var x2_1 = document.createElement('div');
        x2_1.classList.add('panel');
        x2_1.classList.add('panel-default');
        x2_1.innerHTML = "<a data-toggle='collapse' href='#software_configurations_option"+i+"_detail'>Option " + (i+1) + "</a>";

        var x2_1_1 = document.createElement('div');
        x2_1_1.id = 'software_configurations_option'+i+'_detail'
        x2_1_1.classList.add('panel-collapse');
        x2_1_1.classList.add('collapse');
        x2_1_1.innerHTML = "<pre>"+JSON.stringify(software_configurations_avail[tuning_problem_unique_name][i], null, 2)+"</pre>";

        x2_1.appendChild(x2_1_1);
        x2.appendChild(x2_1);

        x.innerHTML = "";
        x.appendChild(x1);
        x.appendChild(x2);

        software_configurations_div.appendChild(x);
    }

    var user_configurations_div = document.getElementById("user_configurations");
    user_configurations_div.innerHTML = "User configurations";
    for (i=0; i<user_configurations_avail[tuning_problem_unique_name].length; i++) {
        var x = document.createElement('div');
        x.classList.add('panel_group');
        x.classList.add('custom-control');
        x.classList.add('custom-checkbox');

        var x1 = document.createElement('input');
        x1.type = 'checkbox';
        x1.classList.add('custom-control-input');
        x1.setAttribute('id', 'user_configurations_option'+i);
        x1.setAttribute('value', JSON.stringify(user_configurations_avail[tuning_problem_unique_name][i], null, 2));
        x1.setAttribute('name', 'user_configurations_list');
        x1.setAttribute('checked', true);

        var x2 = document.createElement('label');
        x2.classList.add('custom-control-label');
        x2.htmlFor = x1.id;

        var x2_1 = document.createElement('div');
        x2_1.classList.add('panel');
        x2_1.classList.add('panel-default');
        x2_1.innerHTML = "<a data-toggle='collapse' href='#user_configurations_option"+i+"_detail'>Option " + (i+1) + " (" + user_configurations_avail[tuning_problem_unique_name][i]["user_name"] + ")</a>";

        var x2_1_1 = document.createElement('div');
        x2_1_1.id = 'user_configurations_option'+i+'_detail'
        x2_1_1.classList.add('panel-collapse');
        x2_1_1.classList.add('collapse');
        x2_1_1.innerHTML = "<pre>"+JSON.stringify(user_configurations_avail[tuning_problem_unique_name][i], null, 2)+"</pre>";

        x2_1.appendChild(x2_1_1);
        x2.appendChild(x2_1);

        x.innerHTML = "";
        x.appendChild(x1);
        x.appendChild(x2);

        user_configurations_div.appendChild(x);
    }

    var search_options_div = document.getElementById("search_options");
    search_options_div.innerHTML = "Search data";
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
        x1.setAttribute("name", "search_options");
        x1.setAttribute("id", "search_options_func_eval");
        x1.setAttribute('checked', true);
        x.appendChild(x1);
        var label1 = document.createElement("label");
        label1.classList.add('custom-control-label');
        label1.innerHTML = 'Function evaluation';
        label1.htmlFor = x1.id;
        x.appendChild(label1);
        search_options_div.appendChild(x);
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
        x1.setAttribute("value", "surrogate_model");
        x1.setAttribute("name", "search_options");
        x1.setAttribute("id", "search_options_surrogate_model");
        x1.setAttribute('checked', true);
        x.appendChild(x1);
        var label1 = document.createElement("label");
        label1.classList.add('custom-control-label');
        label1.innerHTML = 'Surrogate models';
        label1.htmlFor = x1.id;
        x.appendChild(label1);
        search_options_div.appendChild(x);
    }
}

