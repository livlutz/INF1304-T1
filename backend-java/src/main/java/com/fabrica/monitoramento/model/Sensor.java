package com.fabrica.monitoramento.model;

import com.fasterxml.jackson.annotation.JsonProperty;

public class Sensor {

    private SensorValue temperatura;

    private SensorValue vibracao;

    @JsonProperty("consumo_energia")
    private SensorValue consumoEnergia;

    public SensorValue getTemperatura() {
        return temperatura;
    }

    public void setTemperatura(SensorValue temperatura) {
        this.temperatura = temperatura;
    }

    public SensorValue getVibracao() {
        return vibracao;
    }

    public void setVibracao(SensorValue vibracao) {
        this.vibracao = vibracao;
    }

    public SensorValue getConsumoEnergia() {
        return consumoEnergia;
    }

    public void setConsumoEnergia(SensorValue consumoEnergia) {
        this.consumoEnergia = consumoEnergia;
    }

    @Override
    public String toString() {
        return "Sensor{" +
                "temperatura=" + temperatura +
                ", vibracao=" + vibracao +
                ", consumoEnergia=" + consumoEnergia +
                '}';
    }
}
