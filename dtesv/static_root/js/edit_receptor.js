$(document).ready(function() {
   // console.log("inicia");
    function aplicarMascara() {
      //  console.log("funcion");
        var tipoDocumento = $('#id_tipodocumento').val();
        var numDocumentoInput = $('input[name="numdocumento"]');
       // console.log(tipoDocumento);    
        // Intenta quitar la máscara si ya está aplicada antes de volver a aplicarla
        try {
            numDocumentoInput.unmask();
        } catch (e) {
            console.log(e);
            // Captura cualquier error si unmask() no está disponible o no se puede ejecutar
        }

        if (tipoDocumento === "13") {
           // console.log("DUI"); 
            numDocumentoInput.mask('00000000-0');
        } else if (tipoDocumento === "36") {
           // console.log("NIT"); 
            numDocumentoInput.mask('0000-000000-000-0');
        }
    }

    aplicarMascara();

    $('#id_tipodocumento').change(function() {
        aplicarMascara();
    });
});
