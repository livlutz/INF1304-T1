package com.fabrica.monitoramento.service;

import com.fabrica.monitoramento.model.SensorData;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.FileReader;
import java.io.IOException;
import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

public class KafkaConsumerService {

    private static final Logger logger = LoggerFactory.getLogger(KafkaConsumerService.class);
    private final KafkaConsumer<String, String> consumer;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public KafkaConsumerService() throws IOException {
        Properties props = new Properties();
        props.load(new FileReader("src/main/resources/application.properties"));
        this.consumer = new KafkaConsumer<>(props);
    }

    public void consume() {
        consumer.subscribe(Collections.singletonList("dados-sensores"));
        logger.info("Consumer started, subscribed to topic 'dados-sensores'");

        while (true) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            for (ConsumerRecord<String, String> record : records) {
                try {
                    SensorData sensorData = objectMapper.readValue(record.value(), SensorData.class);
                    process(sensorData);
                } catch (IOException e) {
                    logger.error("Error deserializing message: " + record.value(), e);
                }
            }
        }
    }

    private void process(SensorData sensorData) {
        // Simple processing: log the received data
        logger.info("Received sensor data: {}", sensorData);
        detecta_anomalias(sensorData);

    }

    /**
     * Detecta anomalias nos dados dos sensores e ajusta os valores conforme necessário.
     * @param sensorData
     */
    private void detecta_anomalias(SensorData sensorData) {

        final float temperatura = sensorData.getSensores().getTemperatura().getValor();
        final float vibracao = sensorData.getSensores().getVibracao().getValor();
        final float consumoEnergia = sensorData.getSensores().getConsumoEnergia().getValor();
        final int idMaquina = sensorData.getIdMaquina();
        final String setor = sensorData.getSetor();


        if (temperatura > 50) {
            logger.warn("High temperature detected! Machine: {}, Sector: {}, Temperature: {}. Lowering temperature to 50.",
                    idMaquina, setor, temperatura);
            //setar a temperatura para 50
            sensorData.getSensores().getTemperatura().setValor(50);
        }

        if(temperatura < 10){
            logger.warn("Low temperature detected! Machine: {}, Sector: {}, Temperature: {}. Raising temperature to 10.",
                    idMaquina, setor, temperatura);
            //setar a temperatura para 10
            sensorData.getSensores().getTemperatura().setValor(10);
        }

        if (vibracao > 4.0) {
            logger.warn("High vibration detected! Machine: {}, Sector: {}, Vibration: {}. Lowering vibration to 4.0.",
                    idMaquina, setor, vibracao);
            //setar a vibracao para 4.0
            sensorData.getSensores().getVibracao().setValor(4.0);
        }

        if (consumoEnergia > 400.0) {
            logger.warn("High energy consumption detected! Machine: {}, Sector: {}, Energy Consumption: {}. Lowering energy consumption to 400.0.",
                    idMaquina, setor, consumoEnergia);
            //setar o consumo de energia para 400.0
            sensorData.getSensores().getConsumoEnergia().setValor(400.0);
        }

        if(vibracao < 1.0){
            logger.warn("Low vibration detected! Machine: {}, Sector: {}, Vibration: {}. Raising vibration to 1.0.",
                    idMaquina, setor, vibracao);
            //setar a vibracao para 1.0
            sensorData.getSensores().getVibracao().setValor(1.0);
        }

        if(consumoEnergia < 100.0){
            logger.warn("Low energy consumption detected! Machine: {}, Sector: {}, Energy Consumption: {}. Raising energy consumption to 100.0.",
                    idMaquina, setor, consumoEnergia);
            //setar o consumo de energia para 100.0
            sensorData.getSensores().getConsumoEnergia().setValor(100.0);
        }

    }
}
