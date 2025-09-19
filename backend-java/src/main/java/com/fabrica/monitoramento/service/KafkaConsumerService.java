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
     * Constrói um KafkaConsumerService e inicializa o consumidor Kafka.
     * 
     * @throws IOException se houver um erro ao carregar as propriedades de configuração
     */
    public KafkaConsumerService() throws IOException {
        // Carrega a configuração do consumidor Kafka do arquivo de propriedades
        Properties props = new Properties();
        props.load(new FileReader("src/main/resources/application.properties"));
        this.consumer = new KafkaConsumer<>(props);
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
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
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
     * Este método registra os dados recebidos e realiza a detecção básica de anomalias.
     * 
     * @param sensorData os dados do sensor a serem processados
     */
    private void process(SensorData sensorData) {
        // Registra os dados do sensor recebidos
        logger.info("Dados do sensor recebidos: {}", sensorData);

        // Detecção simples de anomalias: verifica temperatura alta
        if (sensorData.getSensores().getTemperatura().getValor() > 50) {
            logger.warn("Temperatura alta detectada! Máquina: {}, Temperatura: {}",
                    sensorData.getIdMaquina(), sensorData.getSensores().getTemperatura().getValor());
        }
    }
}
