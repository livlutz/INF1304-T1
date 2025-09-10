package br.com.trab1;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import java.time.Duration;
import java.util.Collections;
import java.util.Properties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
//import br.com.trab1.WebSocketServer;

/**
 * Classe dos Consumidores, componente do "mini-mundo" simulados por meio de aplicações Java
 * que consomem mensagens do tópico dados-sensores e
 * processam os dados, detectando anomalias.
 */
public class data_consumer{

    public data_consumer(){}
    
    public static void main(String[] args){
        data_consumer consumer = new data_consumer();
    }
}
