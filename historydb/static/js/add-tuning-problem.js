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
    software_div.style.paddingLeft = '20px';
    software_div.style.paddingRight = '20px';
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
    software_div.appendChild(label);

    var version_split_div = document.createElement('div');
    version_split_div.classList.add('custom-control');
    version_split_div.classList.add('custom-radio');
    var version_split = document.createElement('input');
    version_split.id = 'version_split_' + i;
    version_split.type = 'radio';
    version_split.classList.add('custom-control-input');
    version_split.setAttribute('name', 'software_type'+i);
    version_split.setAttribute('value', 'version_split');
    version_split.setAttribute('checked', true);
    var label_ = document.createElement('label');
    label_.classList.add('custom-control-label');
    label_.htmlFor = version_split.id;
    label_.innerHTML = 'Version split number in 3d vector (e.g. [major, minor, revision])';
    version_split_div.appendChild(version_split);
    version_split_div.appendChild(label_);
    software_div.appendChild(version_split_div);

    var version_text_div = document.createElement('div');
    version_text_div.classList.add('custom-control');
    version_text_div.classList.add('custom-radio');
    var version_text = document.createElement('input');
    version_text.id = 'version_text_' + i;
    version_text.type = 'radio';
    version_text.classList.add('custom-control-input');
    version_text.classList.add('mb-3');
    version_text.setAttribute('name', 'software_type'+i);
    version_text.setAttribute('value', 'version_text');
    var label_ = document.createElement('label');
    label_.classList.add('custom-control-label');
    label_.classList.add('mb-3');
    label_.htmlFor = version_text.id;
    label_.innerHTML = 'Text value (e.g. git/svn commit ID, dataset name)';
    version_text_div.appendChild(version_text);
    version_text_div.appendChild(label_);
    software_div.appendChild(version_text_div);

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
