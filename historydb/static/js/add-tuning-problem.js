// Author: Younghyun Cho <younghyun@berkeley.edu>

function UpdateSelectedCategory(element, data_selected)
{
  var selected_category = document.getElementById('selected_category');
  selected_category.innerHTML = "Selected: ";
  if (data_selected.length > 0) {
    selected_category.innerHTML += data_selected[0];
    for (var i = 1; i < data_selected.length; i++) {
      selected_category.innerHTML += ", "+data_selected[i];
    }
  }

  document.getElementById('category_info').innerHTML = "";

  for (var i = 0; i < data_selected.length; i++) {
    var category_div = document.createElement('div');
    category_div.classList.add('mb-3');
    category_div.style.padding = '10px';
    category_div.style.backgroundColor = '#f1f1f1';
    category_div.innerHTML = "";

    var label = document.createElement('label');
    label.innerHTML = "Selected category";
    var category = document.createElement('input');
    category.type = 'text';
    category.classList.add('form-control');
    category.setAttribute('name', 'category_name');
    category.setAttribute('value', data_selected[i]);
    category.setAttribute('readonly', true);
    category.setAttribute('required', true);

    category_div.appendChild(label);
    category_div.appendChild(category);

    document.getElementById('category_info').appendChild(category_div);
  }
}

function UpdateSelectedSoftware(element, data_selected)
{
  var selected_software = document.getElementById('selected_software');
  selected_software.innerHTML = "Selected: ";
  if (data_selected.length > 0) {
    selected_software.innerHTML += data_selected[0];
    for (var i = 1; i < data_selected.length; i++) {
      selected_software.innerHTML += ", "+data_selected[i];
    }
  }

  document.getElementById('software_info').innerHTML = "";

  for (var i = 0; i < data_selected.length; i++) {
    var software_div = document.createElement('div');
    software_div.classList.add('mb-3');
    software_div.style.padding = '10px';
    software_div.style.backgroundColor = '#f1f1f1';
    software_div.innerHTML = "";

    var label = document.createElement('label');
    label.innerHTML = "Selected required software information";
    var software = document.createElement('input');
    software.type = 'text';
    software.classList.add('form-control');
    software.setAttribute('name', 'software_name');
    software.setAttribute('value', data_selected[i]);
    software.setAttribute('readonly', true);
    software.setAttribute('required', true);

    software_div.appendChild(label);
    software_div.appendChild(software);

    var options_div = document.createElement('div');
    var label = document.createElement('label');
    label.innerHTML = "Which type of information is needed?";
    var options = document.createElement('select');
    options.classList.add('custom-select');
    options.setAttribute('name', 'software_type');
    var op = document.createElement('option');
    op.setAttribute('value', '');
    op.setAttribute('label', 'Choose...');
    options.appendChild(op);
    var op = document.createElement('option');
    op.setAttribute('value', 'version_split');
    op.setAttribute('label', 'version split number (e.g. major/minor/revision)');
    options.appendChild(op);
    var op = document.createElement('option');
    op.setAttribute('value', 'version');
    op.setAttribute('label', 'any kind of number (e.g. any type of version number)');
    options.appendChild(op);
    var op = document.createElement('option');
    op.setAttribute('value', 'text');
    op.setAttribute('label', 'any text value (e.g. git/svn commit ID, dataset name)');
    options.appendChild(op);

    options_div.appendChild(label);
    options_div.appendChild(options);

    software_div.appendChild(options_div);

    //var option_div = document.createElement('div');
    //option_div.classList.add('panel_group');
    //option_div.classList.add('custom-control');
    //option_div.classList.add('custom-checkbox');
    //var option1 = document.createElement('input');
    //option1.type = 'checkbox';
    //option1.classList.add('custom-control-input');
    //option1.setAttribute('id', 'option1');
    //option1.setAttribute('value', 'option1');
    //option1.setAttribute('name', 'software_info_type');
    //var option1_label = document.createElement('label');
    //option1_label.classList.add('custom-control-label');
    //option1_label.htmlFor = option1.id;
    //option1_label.innerHTML = "Version";

    //option_div.appendChild(option1);
    //option_div.appendChild(option1_label);

    //var option2 = document.createElement('input');
    //option2.type = 'checkbox';
    //option2.classList.add('custom-control-input');
    //option2.setAttribute('id', 'option2');
    //option2.setAttribute('value', 'option2');
    //option2.setAttribute('name', 'software_info_type');
    //var option2_label = document.createElement('label');
    //option2_label.classList.add('custom-control-label');
    //option2_label.htmlFor = option2.id;
    //option2_label.innerHTML = "Version";

    //option_div.appendChild(option2);
    //option_div.appendChild(option2_label);

    //software_div.appendChild(option_div);

    document.getElementById('software_info').appendChild(software_div);
    //document.getElementById('software_info').appendChild(option_div);
  }
}
