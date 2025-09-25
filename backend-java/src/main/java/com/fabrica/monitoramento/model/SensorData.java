package com.fabrica.monitoramento.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Representa os dados do sensor, incluindo ID da máquina, setor, timestamp e valores dos sensores.
 */
public class SensorData {

    /**
     * ID da máquina.
     * Mapeado da propriedade JSON "id_maquina".
     */
    @JsonProperty("id_maquina")
    private String idMaquina;

    /**
     * Setor onde a máquina está localizada.
     */
    private String setor;

    /**
     * Timestamp de quando os dados foram registrados.
     */
    private String timestamp;

    /**
     * Valores dos sensores, incluindo temperatura, vibração e consumo de energia.
     */
    private Sensor sensores;

    /**
     * Obtém o ID da máquina.
     * 
     * @return o ID da máquina
     */
    public String getIdMaquina() {
        return idMaquina;
    }

    /**
     * Define o ID da máquina.
     * 
     * @param idMaquina o ID da máquina a ser definido
     */
    public void setIdMaquina(String idMaquina) {
        this.idMaquina = idMaquina;
    }

    /**
     * Obtém o setor onde a máquina está localizada.
     * 
     * @return o setor
     */
    public String getSetor() {
        return setor;
    }

    /**
     * Define o setor onde a máquina está localizada.
     * 
     * @param setor o setor a ser definido
     */
    public void setSetor(String setor) {
        this.setor = setor;
    }

    /**
     * Obtém o timestamp de quando os dados foram registrados.
     * 
     * @return o timestamp
     */
    public String getTimestamp() {
        return timestamp;
    }

    /**
     * Define o timestamp de quando os dados foram registrados.
     * 
     * @param timestamp o timestamp a ser definido
     */
    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }

    /**
     * Obtém os valores dos sensores.
     * 
     * @return os valores dos sensores
     */
    public Sensor getSensores() {
        return sensores;
    }

    /**
     * Define os valores dos sensores.
     * 
     * @param sensores os valores dos sensores a serem definidos
     */
    public void setSensores(Sensor sensores) {
        this.sensores = sensores;
    }

    @Override
    public String toString() {
        return "SensorData{" +
                "idMaquina='" + idMaquina + "'" +
                ", setor='" + setor + "'" +
                ", timestamp='" + timestamp + "'" +
                ", sensores=" + sensores +
                '}';
    }
}
