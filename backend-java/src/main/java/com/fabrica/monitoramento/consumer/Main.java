package com.fabrica.monitoramento.consumer;

import java.io.IOException;

import com.fabrica.monitoramento.service.KafkaConsumerService;

public class Main {

    public static void main(String[] args) {
        try {
            KafkaConsumerService consumerService = new KafkaConsumerService();
            consumerService.consume();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
