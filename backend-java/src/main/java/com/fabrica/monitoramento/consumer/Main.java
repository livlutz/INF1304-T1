package com.fabrica.monitoramento.consumer;

import java.io.IOException;

import com.fabrica.monitoramento.service.KafkaConsumerService;

/**
 * Classe principal para a aplicação consumidora de Kafka.
 * Esta aplicação consome dados de sensores de um tópico Kafka e os processa.
 */
public class Main {

    /**
     * Método principal para iniciar o serviço consumidor de Kafka.
     * 
     * @param args argumentos de linha de comando (não utilizados nesta aplicação)
     */
    public static void main(String[] args) {
        try {
            // Inicializa e inicia o serviço consumidor de Kafka
            KafkaConsumerService consumerService = new KafkaConsumerService();
            consumerService.consume();
        } catch (IOException e) {
            // Registra a exceção se houver um problema ao iniciar o serviço consumidor
            e.printStackTrace();
        }
    }
}
