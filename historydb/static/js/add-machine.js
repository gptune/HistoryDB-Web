// Author: Younghyun Cho <younghyun@berkeley.edu>

function UpdateSelectedSystemModels(element, data_selected)
{
  var selected_system_models = document.getElementById('selected_system_models');
  selected_system_models.innerHTML = "Selected: ";
  if (data_selected.length > 0) {
    selected_system_models.innerHTML += data_selected[0];
    for (var i = 1; i < data_selected.length; i++) {
      selected_system_models.innerHTML += ", "+data_selected[i];
    }
  }

  document.getElementById('system_model_info').innerHTML = "";

  for (var i = 0; i < data_selected.length; i++) {
    var system_model_div = document.createElement('div');
    system_model_div.classList.add('mb-3');
    system_model_div.style.padding = '10px';
    system_model_div.style.paddingLeft = '20px';
    system_model_div.style.paddingRight = '20px';
    system_model_div.style.backgroundColor = '#f1f1f1';
    system_model_div.innerHTML = "";

    var label = document.createElement('label');
    label.innerHTML = "Selected system model";
    var system_model = document.createElement('input');
    system_model.type = 'text';
    system_model.classList.add('form-control');
    system_model.classList.add('mb-3');
    system_model.setAttribute('name', 'system_model_name');
    system_model.setAttribute('value', data_selected[i]);
    system_model.setAttribute('readonly', true);
    system_model.setAttribute('required', true);

    system_model_div.appendChild(label);
    system_model_div.appendChild(system_model);

    var label = document.createElement('label');
    label.innerHTML = "Tag names that can be used instead of the given full name (comma separated)";
    var tags = document.createElement('input');
    tags.type = 'text';
    tags.classList.add('form-control');
    tags.classList.add('mb-3');
    tags.setAttribute('name', 'system_model_tags');

    system_model_div.appendChild(label);
    system_model_div.appendChild(tags);

    document.getElementById('system_model_info').appendChild(system_model_div);
  }
}

function UpdateSelectedProcessorModels(element, data_selected)
{
  var selected_processor_models_div = document.getElementById('selected_processor_models_div');
  selected_processor_models_div.innerHTML = "Selected: ";
  if (data_selected.length > 0) {
    selected_processor_models_div.innerHTML += data_selected[0];
    for (var i = 1; i < data_selected.length; i++) {
      selected_processor_models_div.innerHTML += ", "+data_selected[i];
    }
  }

  document.getElementById('processor_model_info').innerHTML = "";

  for (var i = 0; i < data_selected.length; i++) {
    var processor_info_div = document.createElement('div');
    processor_info_div.classList.add('mb-3');
    processor_info_div.style.backgroundColor = '#f1f1f1';
    processor_info_div.style.padding = '10px';
    processor_info_div.style.paddingLeft = '20px';
    processor_info_div.style.paddingRight = '20px';
    processor_info_div.innerHTML = "";

    var processor_model_div = document.createElement('div');
    processor_model_div.classList.add('mb-3');
    var label = document.createElement('label');
    label.innerHTML = "Selected processor model";
    var processor_model = document.createElement('input');
    processor_model.type = 'text';
    processor_model.classList.add('form-control');
    processor_model.setAttribute('name', 'processor_model_name');
    processor_model.setAttribute('value', data_selected[i]);
    processor_model.setAttribute('readonly', true);
    processor_model.setAttribute('required', true);
    processor_model_div.appendChild(label);
    processor_model_div.appendChild(processor_model);
    processor_info_div.appendChild(processor_model_div);

    var processor_info1 = document.createElement('div');
    processor_info1.classList.add('row');

    var processor_info1_col1 = document.createElement('div');
    processor_info1_col1.classList.add('col');
    var label = document.createElement('label');
    label.innerHTML = "Number of total nodes";
    var num_nodes = document.createElement('input');
    num_nodes.type = 'number';
    num_nodes.classList.add('form-control');
    num_nodes.classList.add('mb-3');
    num_nodes.setAttribute('name', 'num_nodes');
    processor_info1_col1.appendChild(label);
    processor_info1_col1.appendChild(num_nodes);

    var processor_info1_col2 = document.createElement('div');
    processor_info1_col2.classList.add('col');
    var label = document.createElement('label');
    label.innerHTML = "Number of total cores";
    var num_cores = document.createElement('input');
    num_cores.type = 'number';
    num_cores.classList.add('form-control');
    num_cores.classList.add('mb-3');
    num_cores.setAttribute('name', 'num_cores');
    processor_info1_col2.appendChild(label);
    processor_info1_col2.appendChild(num_cores);

    processor_info1.appendChild(processor_info1_col1);
    processor_info1.appendChild(processor_info1_col2);
    processor_info_div.appendChild(processor_info1);

    var processor_info2 = document.createElement('div');
    processor_info2.classList.add('row');

    var processor_info1_col1 = document.createElement('div');
    processor_info1_col1.classList.add('col');
    var label = document.createElement('label');
    label.innerHTML = "Number of sockets per node";
    var num_sockets = document.createElement('input');
    num_sockets.type = 'number';
    num_sockets.classList.add('form-control');
    num_sockets.classList.add('mb-3');
    num_sockets.setAttribute('name', 'num_sockets');
    processor_info1_col1.appendChild(label);
    processor_info1_col1.appendChild(num_sockets);

    var processor_info1_col2 = document.createElement('div');
    processor_info1_col2.classList.add('col');
    var label = document.createElement('label');
    label.innerHTML = "Memory size per node (GB)";
    var memory_size = document.createElement('input');
    memory_size.type = 'number';
    memory_size.classList.add('form-control');
    memory_size.classList.add('mb-3');
    memory_size.setAttribute('name', 'memory_size');
    processor_info1_col2.appendChild(label);
    processor_info1_col2.appendChild(memory_size);

    processor_info2.appendChild(processor_info1_col1);
    processor_info2.appendChild(processor_info1_col2);
    processor_info_div.appendChild(processor_info2);

    var label = document.createElement('label');
    label.innerHTML = "Tag names that can be used instead of the given full name (comma separated)";
    var tags = document.createElement('input');
    tags.type = 'text';
    tags.classList.add('form-control');
    tags.classList.add('mb-3');
    tags.setAttribute('name', 'processor_model_tags');

    processor_info_div.appendChild(label);
    processor_info_div.appendChild(tags);

    document.getElementById('processor_model_info').appendChild(processor_info_div);
  }
}

function UpdateSelectedInterconnect(element, data_selected)
{
  var selected_interconnects_div = document.getElementById('selected_interconnects');
  selected_interconnects_div.innerHTML = "Selected: ";
  if (data_selected.length > 0) {
    selected_interconnects_div.innerHTML += data_selected[0];
    for (var i = 1; i < data_selected.length; i++) {
      selected_interconnects_div.innerHTML += ", "+data_selected[i];
    }
  }

  document.getElementById('interconnect_info').innerHTML = "";

  for (var i = 0; i < data_selected.length; i++) {
    var interconnect_div = document.createElement('div');
    interconnect_div.classList.add('mb-3');
    interconnect_div.style.padding = '10px';
    interconnect_div.style.paddingLeft = '20px';
    interconnect_div.style.paddingRight = '20px';
    interconnect_div.style.backgroundColor = '#f1f1f1';
    interconnect_div.innerHTML = "";

    var label = document.createElement('label');
    label.innerHTML = "Selected interconnect";
    var interconnect = document.createElement('input');
    interconnect.type = 'text';
    interconnect.classList.add('form-control');
    interconnect.classList.add('mb-3');
    interconnect.setAttribute('name', 'interconnect_name');
    interconnect.setAttribute('value', data_selected[i]);
    interconnect.setAttribute('readonly', true);
    interconnect.setAttribute('required', true);

    interconnect_div.appendChild(label);
    interconnect_div.appendChild(interconnect);

    var label = document.createElement('label');
    label.innerHTML = "Tag names that can be used instead of the given full name (comma separated)";
    var tags = document.createElement('input');
    tags.type = 'text';
    tags.classList.add('form-control');
    tags.classList.add('mb-3');
    tags.setAttribute('name', 'interconnect_tags');

    interconnect_div.appendChild(label);
    interconnect_div.appendChild(tags);

    document.getElementById('interconnect_info').appendChild(interconnect_div);
  }

}

function AddInputDivField(input_div_id, input_div_name) {
  var input_div = document.getElementById(input_div_id);

  var num_inputs = document.getElementsByName(input_div_name).length+1;

  clone = input_div.cloneNode(true);
  clone.id = input_div_id + '_' + num_inputs;
  inputs = clone.getElementsByTagName('input');
  for (var z=0; z<inputs.length; z++)
    inputs[z].value = "";
  input_div.parentNode.appendChild(clone);
}

function RemoveInputDivField(input_div_id, input_div_name) {
  var num_inputs = document.getElementsByName(input_div_name).length;
  document.getElementById(input_div_id+'_'+num_inputs).remove();
}

function UpdateSystemModel(element, selectedIndex, system_models_map)
{
  system_model_select_panel = element.parentNode.getElementsByTagName('select');
  if (system_model_select_panel.length > 1) {
    system_model_select_panel[1].remove();
  }

  var select = document.createElement('select');
  select.classList.add('custom-select');
  select.classList.add('d-block');
  select.classList.add('w-100');
  select.name = 'system_model';
  var option = document.createElement('option');
  option.value = '';
  option.label = "Choose...";
  select.appendChild(option);

  var system_model_div = document.createElement('div');
  system_model_div.appendChild(select);

  system_model_selected = element.options[selectedIndex].value;
  for (var i = 0; i < system_models_map[system_model_selected].length; i++) {
    var option = document.createElement('option');
    option.label = system_models_map[system_model_selected][i];
    option.value = system_models_map[system_model_selected][i];
    select.appendChild(option);
  }

  element.parentNode.appendChild(system_model_div);
}

function UpdateProcessorMapDepp(element, selectedIndex, processors_map)
{
  alert("ASDFASDFASFASDF");
  alert(selectedIndex);
  alert(JSON.stringify(processors_map));
  alert(element.options[selectedIndex]);
  alert(processors_map[selectedIndex]);
}

//function UpdateProcessorMap(element, selectedIndex, processors_map)
function UpdateProcessorMap(element, processors_map)
{
  alert('1234');
  alert(processors_map)
  //system_model_select_panel = element.parentNode.getElementsByTagName('select');
  //if (system_model_select_panel.length > 1) {
  //  system_model_select_panel[1].remove();
  //}

  var select = document.createElement('select');
  select.classList.add('custom-select');
  select.classList.add('d-block');
  select.classList.add('w-100');
  select.setAttribute('onChange', "UpdateProcessorMap(this, '1234');");
    //this.selectedIndex, processors_map[element.options[selectedIndex].value]);"); //"UpdateProcessorMap(this, this.selectedIndex, processors_map);");
  var option = document.createElement('option');
  option.value = '';
  option.label = "Choose...";
  select.appendChild(option);

  //var processors_map_selected = element.options[selectedIndex].value;
  //const keys = Object.keys(processors_map[processors_map_selected]);
  const keys = Object.keys(processors_map);
  for (var key in keys) {
    var option = document.createElement('option');
    option.label = keys[key];
    option.value = keys[key];
    select.appendChild(option);
  }

  element.parentNode.appendChild(select);

  alert('####');



//  var select = document.createElement('select');
//  select.classList.add('custom-select');
//  select.classList.add('d-block');
//  select.classList.add('w-100');
//  select.name = 'system_model';
//  var option = document.createElement('option');
//  option.value = '';
//  option.label = "Choose...";
//  select.appendChild(option);
//
//  var system_model_div = document.createElement('div');
//  system_model_div.appendChild(select);
//
//  system_model_selected = element.options[selectedIndex].value;
//  for (var i = 0; i < system_models_map[system_model_selected].length; i++) {
//    var option = document.createElement('option');
//    option.label = system_models_map[system_model_selected][i];
//    option.value = system_models_map[system_model_selected][i];
//    select.appendChild(option);
//  }
//
//  element.parentNode.appendChild(system_model_div);
}
