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

        // Anomaly detection
        if (sensorData.getSensores().getTemperatura().getValor() > 50) {
            logger.warn("High temperature detected! Machine: {}, Temperature: {}",
                    sensorData.getIdMaquina(), sensorData.getSensores().getTemperatura().getValor());
        }
    }
}
