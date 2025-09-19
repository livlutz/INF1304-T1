package com.fabrica.monitoramento.model;

public class SensorValue {

    private double valor;

    private String unidade;

    public double getValor() {
        return valor;
    }

    public void setValor(double valor) {
        this.valor = valor;
    }

    public String getUnidade() {
        return unidade;
    }

    public void setUnidade(String unidade) {
        this.unidade = unidade;
    }

    @Override
    public String toString() {
        return "SensorValue{" +
                "valor=" + valor +
                ", unidade='" + unidade + "'" +
                '}';
    }
}
