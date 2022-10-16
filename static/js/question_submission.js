let numAnswers;
let answers;
let numSelector;

let wrapper = document.createElement('div');
let label = document.createElement('label');
wrapper.className = "form-group";

let numAnswers = 1;
answers = document.createElement('div');

let qLabel = document.createElement('label');
qLabel.innerText = "Question:";
qLabel.htmlFor = "McQ";

let mcQ = document.createElement('input');
mcQ.type = 'text';
mcQ.id = "McQ";
mcQ.name = "McQ";
mcQ.className = 'form-control';

label.innerText = "Number of Options"
label.htmlFor = "numOptions";

numSelector = document.createElement("select");
for( let k = 0; k < 10; k++ )
{
    let temp = document.createElement('option');
    temp.innerText = (k + 1).toString();
    numSelector.append(temp);
}

numSelector.name = "McNumAnswers" + i;
numSelector.id = "McNumAnswers" + i;
numSelector.onchange = function ()
{
    numAnswers = parseInt(numSelector.value);
    console.log(numAnswers);
    answers.innerHTML = "";

    for(let j = 0; j < numAnswers; j++)
    {
        var tempWrap = document.createElement('div');
        tempWrap.className = 'row';

        var tempLabel = document.createElement("label");
        tempLabel.htmlFor = "McA" + j;
        tempLabel.innerText = "Answer  " + (j + 1);

        tempWrap.append(tempLabel);

        var tempInput = document.createElement('input');
        tempInput.type = 'text';
        tempInput.id = 'McA' + j;
        tempInput.name = 'McA' + j;

        tempWrap.append(tempInput);

        var tempCorrect = document.createElement('input');
        tempCorrect.type = 'checkbox';
        tempCorrect.id = 'McC' + j;
        tempCorrect.name = "McC" + j;

        tempWrap.append(tempCorrect);

        answers.append(tempWrap);
    }
}

wrapper.append(qLabel);
wrapper.append(mcQ);
wrapper.append(label);
wrapper.append(numSelector);
wrapper.append(answers);