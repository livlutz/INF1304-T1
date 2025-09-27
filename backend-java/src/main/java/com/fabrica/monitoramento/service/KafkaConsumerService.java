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
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Classe de serviço para consumir dados de sensores do Kafka.
 * Esta classe lida com a configuração do consumidor Kafka, consumo de mensagens
 * e processamento dos dados dos sensores.
 */
public class KafkaConsumerService {

    /**
     * Logger para esta classe.
     */
    private static final Logger logger = LoggerFactory.getLogger(KafkaConsumerService.class);

    /**
     * Instância do consumidor Kafka.
     */
    private final KafkaConsumer<String, String> consumer;

    /**
     * ObjectMapper para desserializar mensagens JSON.
     */
    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Pool de threads para processar anomalias.
     */
    private final ExecutorService executorService;

    /**
     * Constrói um KafkaConsumerService e inicializa o consumidor Kafka e o pool de threads.
     *
     * @throws IOException se houver um erro ao carregar as propriedades de configuração
     */
    public KafkaConsumerService() throws IOException {
        // Carrega a configuração do consumidor Kafka do arquivo de propriedades
        Properties props = new Properties();
        props.load(new FileReader("src/main/resources/application.properties"));
        this.consumer = new KafkaConsumer<>(props);
        this.executorService = Executors.newFixedThreadPool(10);
    }

    /**
     * Inicia o consumo de mensagens do tópico Kafka.
     * Este método se inscreve no tópico "dados-sensores" e continuamente faz polling por novas mensagens.
     * Cada mensagem é desserializada e processada.
     */
    public void consume() {
        // Inscreve-se no tópico Kafka
        consumer.subscribe(Collections.singletonList("dados-sensores"));
        logger.info("Consumidor iniciado, inscrito no tópico 'dados-sensores'");

        // Continuamente faz polling por novas mensagens
        while (true) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ZERO);
            for (ConsumerRecord<String, String> record : records) {
                try {
                    // Desserializa a mensagem JSON para um objeto SensorData
                    SensorData sensorData = objectMapper.readValue(record.value(), SensorData.class);
                    process(sensorData);
                } catch (IOException e) {
                    // Registra quaisquer erros de desserialização
                    logger.error("Erro ao desserializar a mensagem: " + record.value(), e);
                }
            }
        }
    }

    /**
     * Processa os dados do sensor recebidos.
     * Este método registra os dados recebidos e realiza a detecção de anomalias.
     *
     * @param sensorData os dados do sensor a serem processados
     */
    private void process(SensorData sensorData) {
        // Simple processing: log the received data
        logger.info("Received sensor data: {}", sensorData);
        detecta_anomalias(sensorData);
    }

    /**
     * Detecta anomalias nos dados dos sensores e submete o tratamento para threads separadas.
     * @param sensorData
     */
    private void detecta_anomalias(SensorData sensorData) {
        final double temperatura = sensorData.getSensores().getTemperatura().getValor();
        final double vibracao = sensorData.getSensores().getVibracao().getValor();
        final double consumoEnergia = sensorData.getSensores().getConsumoEnergia().getValor();

        if (temperatura > 50) {
            executorService.submit(() -> handleHighTemperature(sensorData));
        }
        if (temperatura < 10) {
            executorService.submit(() -> handleLowTemperature(sensorData));
        }
        if (vibracao > 4.0) {
            executorService.submit(() -> handleHighVibration(sensorData));
        }
        if (vibracao < 1.0) {
            executorService.submit(() -> handleLowVibration(sensorData));
        }
        if (consumoEnergia > 400.0) {
            executorService.submit(() -> handleHighEnergyConsumption(sensorData));
        }
        if (consumoEnergia < 100.0) {
            executorService.submit(() -> handleLowEnergyConsumption(sensorData));
        }
    }

    private void handleHighTemperature(SensorData sensorData) {
        logger.warn("High temperature detected! Machine: {}, Sector: {}, Temperature: {}. Lowering temperature to 50.",
                sensorData.getIdMaquina(), sensorData.getSetor(), sensorData.getSensores().getTemperatura().getValor());
        sensorData.getSensores().getTemperatura().setValor(50);
    }

    private void handleLowTemperature(SensorData sensorData) {
        logger.warn("Low temperature detected! Machine: {}, Sector: {}, Temperature: {}. Raising temperature to 10.",
                sensorData.getIdMaquina(), sensorData.getSetor(), sensorData.getSensores().getTemperatura().getValor());
        sensorData.getSensores().getTemperatura().setValor(10);
    }

    private void handleHighVibration(SensorData sensorData) {
        logger.warn("High vibration detected! Machine: {}, Sector: {}, Vibration: {}. Lowering vibration to 4.0.",
                sensorData.getIdMaquina(), sensorData.getSetor(), sensorData.getSensores().getVibracao().getValor());
        sensorData.getSensores().getVibracao().setValor(4.0);
    }

    private void handleLowVibration(SensorData sensorData) {
        logger.warn("Low vibration detected! Machine: {}, Sector: {}, Vibration: {}. Raising vibration to 1.0.",
                sensorData.getIdMaquina(), sensorData.getSetor(), sensorData.getSensores().getVibracao().getValor());
        sensorData.getSensores().getVibracao().setValor(1.0);
    }

    private void handleHighEnergyConsumption(SensorData sensorData) {
        logger.warn("High energy consumption detected! Machine: {}, Sector: {}, Energy Consumption: {}. Lowering energy consumption to 400.0.",
                sensorData.getIdMaquina(), sensorData.getSetor(), sensorData.getSensores().getConsumoEnergia().getValor());
        sensorData.getSensores().getConsumoEnergia().setValor(400.0);
    }

    private void handleLowEnergyConsumption(SensorData sensorData) {
        logger.warn("Low energy consumption detected! Machine: {}, Sector: {}, Energy Consumption: {}. Raising energy consumption to 100.0.",
                sensorData.getIdMaquina(), sensorData.getSetor(), sensorData.getSensores().getConsumoEnergia().getValor());
        sensorData.getSensores().getConsumoEnergia().setValor(100.0);
    }
}
