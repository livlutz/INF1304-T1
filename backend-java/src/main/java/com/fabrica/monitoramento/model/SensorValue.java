package com.fabrica.monitoramento.model;

/**
 * Representa um valor de sensor com um valor numérico e unidade de medida.
 */
public class SensorValue {

    /**
     * Valor numérico da leitura do sensor.
     */
    private double valor;

    /**
     * Unidade de medida para o valor do sensor (por exemplo, "C" para Celsius, "kW" para quilowatts).
     */
    private String unidade;

    /**
     * Obtém o valor numérico da leitura do sensor.
     * 
     * @return o valor numérico
     */
    public double getValor() {
        return valor;
    }

    /**
     * Define o valor numérico da leitura do sensor.
     * 
     * @param valor o valor numérico a ser definido
     */
    public void setValor(double valor) {
        this.valor = valor;
    }

    /**
     * Obtém a unidade de medida para o valor do sensor.
     * 
     * @return a unidade de medida
     */
    public String getUnidade() {
        return unidade;
    }

    /**
     * Define a unidade de medida para o valor do sensor.
     * 
     * @param unidade a unidade de medida a ser definida
     */
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
