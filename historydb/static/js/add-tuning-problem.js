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
    category_div.style.paddingLeft = '20px';
    category_div.style.paddingRight = '20px';
    category_div.innerHTML = "";

    var label = document.createElement('label');
    label.innerHTML = "Selected category";
    var category = document.createElement('input');
    category.type = 'text';
    category.classList.add('form-control');
    category.classList.add('mb-3');
    category.setAttribute('name', 'category_name');
    category.setAttribute('value', data_selected[i]);
    category.setAttribute('readonly', true);
    category.setAttribute('required', true);

    category_div.appendChild(label);
    category_div.appendChild(category);

    var label = document.createElement('label');
    label.innerHTML = "Tag names that can be used instead of the given full name (comma separated)";
    var tags = document.createElement('input');
    tags.type = 'text';
    tags.classList.add('form-control');
    tags.setAttribute('name', 'category_tags');

    category_div.appendChild(label);
    category_div.appendChild(tags);

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
    software.classList.add('mb-3');
    software.setAttribute('name', 'software_name');
    software.setAttribute('value', data_selected[i]);
    software.setAttribute('readonly', true);
    software.setAttribute('required', true);

    software_div.appendChild(label);
    software_div.appendChild(software);

    var label = document.createElement('label');
    label.innerHTML = "Which type of information is needed?";
    var options = document.createElement('select');
    options.classList.add('custom-select');
    options.classList.add('mb-3');
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

    software_div.appendChild(label);
    software_div.appendChild(options);

    var label = document.createElement('label');
    label.innerHTML = "Tag names that can be used instead of the given full name (comma separated)";
    var tags = document.createElement('input');
    tags.type = 'text';
    tags.classList.add('form-control');
    tags.setAttribute('name', 'software_tags');

    software_div.appendChild(label);
    software_div.appendChild(tags);

    document.getElementById('software_info').appendChild(software_div);
  }
}
