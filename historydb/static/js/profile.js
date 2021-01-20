function EditToggle() {
  if (document.getElementById("edit-toggle").checked) {
    document.getElementById("firstname").readOnly = false;
    document.getElementById("lastname").readOnly = false;
    document.getElementById("position").readOnly = false;
    document.getElementById("affiliation").readOnly = false;
    document.getElementById("ecp_member_y").disabled = false;
    document.getElementById("ecp_member_n").disabled = false;
    document.getElementById("ecp_member_x").disabled = false;
    document.getElementById("updateDiv").style.display = "block";
  } else {
    document.getElementById("firstname").readOnly = true;
    document.getElementById("lastname").readOnly = true;
    document.getElementById("position").readOnly = true;
    document.getElementById("affiliation").readOnly = true;
    document.getElementById("ecp_member_y").disabled = true;
    document.getElementById("ecp_member_n").disabled = true;
    document.getElementById("ecp_member_x").disabled = true;
    document.getElementById("updateDiv").style.display = "none";
  }
}
