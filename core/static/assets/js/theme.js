// Custome theme code



$("#add-tipo-de-uso").on('mouseup', ()=>{
    var $values = $('#tipo-de-uso option');

    if($values[0].value != 0) {
        var $newFormGroup = $('<div class="form-group col-md-12"></div>');
        var $inputGroup = $('<div class="input-group"></div>');

        var $value = $('#tipo-de-uso option:selected');
        var $spanText = $('<span class="input-group-text col-md-8"></span>');
        value_text = $value.text() + ' e freq mensal';

        $spanText.prepend(value_text);
        $value.remove();

        $inputGroup.prepend($spanText);


        $inputGroup.append('<input class="form-control com-md-1" type="number" placeholder="Qtd">');
        $inputGroup.append('<input class="form-control com-md-1" type="number" placeholder="Freq">');
        $newFormGroup.prepend($inputGroup);

        $('#AAC-rows').append($newFormGroup);
    }
    if($values.length == 1 && $values[0].value != 0) {

        return $('#tipo-de-uso')
            .append('<option value="0" selected="">Nenhum item</option>');
    }
});

$('#formCheck-1').on('click', ()=>{
    var apt_input = $('#totalApartamentos input');
    apt_input.val('');
    apt_input.prop("disabled", true);
    //$('#totalApartamentos input').prop("disabled", true);
    
});

$('#formCheck-2').on('click', ()=>{    
    $("#totalApartamentos input").prop("disabled", false);
    
});




function addCustomConsumo() {
    function createTextInput(consumoid) {
        var textInput = document.createElement('input');
        textInput.id = `demandas-${consumoid}-nome`;
        textInput.setAttribute("name", `demandas-${consumoid}-nome`)
        textInput.type = "text";
        textInput.className = "form-control";
        textInput.placeholder = "Nome do uso aqui";
        return textInput;
    }

    function createBasicInputGroup() {
        var result = document.createElement('div');
        result.className = 'input-group';

        var append = document.createElement('div')
        append.className = 'input-group-append';

        result.appendChild(append);
        
        return result;
    }

    function createFrequencia(consumoid) {
        var result = createBasicInputGroup()

        var frequencia_input = document.createElement('input')
        frequencia_input.setAttribute("type", "number");
        frequencia_input.setAttribute("name", `demandas-${consumoid}-frequencia_mensal`);
        frequencia_input.setAttribute("min", "1");
        frequencia_input.setAttribute("value", "1");
        frequencia_input.className = "form-control";

        var span_text = document.createElement('span');
        span_text.appendChild(document.createTextNode('vezes ao mês'));
        span_text.className = "input-group-text";
    
        result.prepend(frequencia_input);
        result.childNodes[1].appendChild(span_text);
        console.log(result);
        return result;
    }

    function createUsoFinal(consumoid) {
        var result = createBasicInputGroup();
        var uso_final = document.createElement('input');
        uso_final.setAttribute("type", "number");
        uso_final.setAttribute("name", `demandas-${consumoid}-indicador`);
        uso_final.setAttribute("min", "1");
        uso_final.setAttribute("value", "1");
        uso_final.className = "form-control";

        var span_text = document.createElement('span');
        span_text.appendChild(document.createTextNode('litros/dia'));
        span_text.className = "input-group-text";
        
        result.prepend(uso_final);
        result.childNodes[1].appendChild(span_text);
        return result;
    }
    function createDeleteButton(){
        var delete_button = document.createElement('button');
        delete_button.setAttribute('onclick', "delete_row(this)");
        delete_button.setAttribute('type', 'button');
        delete_button.className = "btn btn-light";
        delete_button.textContent = "Deletar"
        return delete_button
    }

    var newTr = document.createElement('tr');

    var tablecells = [4];
    tablecells[0] = document.createElement('td');
    tablecells[1] = document.createElement('td');
    tablecells[2] = document.createElement('td');
    tablecells[3] = document.createElement('td');
    tablecells[0].appendChild(createTextInput(consumoid));

    tablecells[1].appendChild(createFrequencia(consumoid));

    tablecells[2].appendChild(createUsoFinal(consumoid));
    tablecells[3].appendChild(createDeleteButton());
    
    tablecells.forEach(element => {
        newTr.appendChild(element);
    });

    var table = document.getElementById('consumosTable');
    table.appendChild(newTr);
    consumoid++;
}

function delete_row(e)
{
    e.parentNode.parentNode.parentNode.removeChild(e.parentNode.parentNode);
}

function submit_simulacao() {
    $("#simulacaoForm").submit()
}


var consumoid = 7;
const form = document.getElementById('edificacaoForm');



var newCustomConsumo = document.getElementById('addCustomConsumo');
newCustomConsumo.addEventListener('click', addCustomConsumo, false);

const taxa_de_juros = document.getElementById('id_taxa_de_juros');
const changeCisternaVolume = document.getElementById('change_interval');

taxa_de_juros.addEventListener('change', submit_simulacao, false);

changeCisternaVolume.addEventListener('click', submit_simulacao, false)

document.querySelectorAll('.form-check-input')
    .forEach(checkbox => {
    checkbox.addEventListener('change', submit_simulacao, false)
})
