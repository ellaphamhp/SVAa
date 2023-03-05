//Change the check box accordingly to acquire status:
function updateCheckbox(){
    var docStatus = document.getElementsByClassName("form-check-label");
    var checkBox = document.getElementsByClassName("form-check-input");
    var checkedStatus = document.getElementsByClassName("form-check-status");
    console.log("Start updating checkbox");
    for (let i = 0; i < checkBox.length; i ++){
        if (checkedStatus[i].value == 1) {
            console.log(checkedStatus[i].value);
            checkBox[i].checked = true;
            docStatus[i].style.color = 'green';
        } else {
            console.log(checkedStatus[i].value);
            checkBox[i].checked = false;
            docStatus[i].style.color = 'black';
        }
    };
};


//application.html, change color of text when the required doc is prepared:
function validate(){
    var docStatus = document.getElementsByClassName("form-check-label");
    var checkBox = document.getElementsByClassName("form-check-input");
    var checkedVar = document.getElementsByClassName("form-check-var");
    for (let i = 0; i < checkBox.length; i ++){
        if (checkBox[i].checked) {
            docStatus[i].style.color = 'green';
        } else {
            docStatus[i].style.color = 'black';
        }
    };

    for (let i = 0; i < checkBox.length; i ++){
        if (checkBox[i].checked) {
            checkedVar[i].value = 'done';
        } else {
            checkedVar[i].value = 'not done';
        }
    };
};


//Update the input variable to tell whether a requirement is prepared:
function updateProgress(){
    var checkBox = document.getElementsByClassName("form-check-input");
    var checkedVar = document.getElementsByClassName("form-check-var");
    for (let i = 0; i < checkBox.length; i ++){
        if (checkBox[i].checked) {
            checkedVar[i].value = 'done';
        } else {
            checkedVar[i].value = 'not done';
        }
    };
};





