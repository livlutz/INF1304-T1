package com.fabrica.monitoramento.model;

import com.fasterxml.jackson.annotation.JsonProperty;

public class SensorData {

    @JsonProperty("id_maquina")
    private String idMaquina;

    private String setor;

    private String timestamp;

    private Sensor sensores;

    public String getIdMaquina() {
        return idMaquina;
    }

    public void setIdMaquina(String idMaquina) {
        this.idMaquina = idMaquina;
    }

    public String getSetor() {
        return setor;
    }

    public void setSetor(String setor) {
        this.setor = setor;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }

    public Sensor getSensores() {
        return sensores;
    }

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
