function submit_simulacao() {
    $("#simulacaoForm").submit()
}


const taxa_de_juros = document.getElementById('id_taxa_de_juros');
const changeCisternaVolume = document.getElementById('change_interval');

taxa_de_juros.addEventListener('change', submit_simulacao, false);

changeCisternaVolume.addEventListener('click', submit_simulacao, false)

document.querySelectorAll('.form-check-input')
    .forEach(checkbox => {
    checkbox.addEventListener('change', submit_simulacao, false)
})