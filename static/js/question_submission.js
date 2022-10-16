let answers;
let numSelector;

let wrapper = document.createElement('div');
let label = document.createElement('label');
wrapper.className = "form-group";

let numAnswers = 1;
answers = document.createElement('div');

label.innerText = "Number of Options"
label.htmlFor = "numOptions";

numSelector = document.createElement("select");
for( let k = 0; k < 10; k++ )
{
    let temp = document.createElement('option');
    temp.innerText = (k + 1).toString();
    numSelector.append(temp);
}

numSelector.name = "McNumAnswers";
numSelector.id = "McNumAnswers";
function makeOptions()
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
        tempLabel.innerText = "Choice  " + (j + 1);

        tempWrap.append(tempLabel);

        var tempInput = document.createElement('input');
        tempInput.type = 'text';
        tempInput.id = 'McA' + j;
        tempInput.name = 'McA' + j;

        tempWrap.append(tempInput);

        answers.append(tempWrap);
    }
}

numSelector.onchange = makeOptions;

wrapper.append(label);
wrapper.append(numSelector);
wrapper.append(answers);
makeOptions();

$("#other-answers")[0].append(wrapper)
