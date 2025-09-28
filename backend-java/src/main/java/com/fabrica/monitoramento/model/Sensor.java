package com.fabrica.monitoramento.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Representa um sensor com valores de temperatura, vibração e consumo de energia.
 */
public class Sensor {

    /**
     * Valor do sensor de temperatura.
     */
    private SensorValue temperatura;

    /**
     * Valor do sensor de vibração.
     */
    private SensorValue vibracao;

    /**
     * Valor do sensor de consumo de energia.
     * Mapeado da propriedade JSON "consumo_energia".
     */
    @JsonProperty("consumo_energia")
    private SensorValue consumoEnergia;

     /**
     * Valor do sensor de pressão.
     * Mapeado da propriedade JSON "pressao".
     */
    @JsonProperty("pressao")
    private SensorValue pressao;

    /**
     * Valor do sensor de umidade.
     * Mapeado da propriedade JSON "umidade".
     */
    private SensorValue umidade;

    /**
     * Obtém o valor do sensor de temperatura.
     *
     * @return o valor do sensor de temperatura
     */
    public SensorValue getTemperatura() {
        return temperatura;
    }

    /**
     * Define o valor do sensor de temperatura.
     *
     * @param temperatura o valor do sensor de temperatura a ser definido
     */
    public void setTemperatura(SensorValue temperatura) {
        this.temperatura = temperatura;
    }

    /**
     * Obtém o valor do sensor de vibração.
     *
     * @return o valor do sensor de vibração
     */
    public SensorValue getVibracao() {
        return vibracao;
    }

    /**
     * Define o valor do sensor de vibração.
     *
     * @param vibracao o valor do sensor de vibração a ser definido
     */
    public void setVibracao(SensorValue vibracao) {
        this.vibracao = vibracao;
    }

    /**
     * Obtém o valor do sensor de consumo de energia.
     *
     * @return o valor do sensor de consumo de energia
     */
    public SensorValue getConsumoEnergia() {
        return consumoEnergia;
    }

    /**
     * Define o valor do sensor de consumo de energia.
     *
     * @param consumoEnergia o valor do sensor de consumo de energia a ser definido
     */
    public void setConsumoEnergia(SensorValue consumoEnergia) {
        this.consumoEnergia = consumoEnergia;
    }

    /**
     * Obtém o valor do sensor de pressão.
     *
     * @return o valor do sensor de pressão
     */
    public SensorValue getPressao() {
        return pressao;
    }

    /**
     * Define o valor do sensor de pressão.
     *
     * @param pressao o valor do sensor de pressão a ser definido
     */
    public void setPressao(SensorValue pressao) {
        this.pressao = pressao;
    }

    /**
     * Obtém o valor do sensor de umidade.
     *
     * @return o valor do sensor de umidade
     */
    public SensorValue getUmidade() {
        return umidade;
    }

    /**
     * Define o valor do sensor de umidade.
     *
     * @param umidade o valor do sensor de umidade a ser definido
     */
    public void setUmidade(SensorValue umidade) {
        this.umidade = umidade;
    }

    @Override
    public String toString() {
        return "Sensor{" +
                "temperatura=" + temperatura +
                ", vibracao=" + vibracao +
                ", consumoEnergia=" + consumoEnergia +
                ", pressao=" + pressao +
                ", umidade=" + umidade +
                '}';
    }
}
