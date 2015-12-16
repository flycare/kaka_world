
-- 玩家成就(未使用)
-- Table: achievement

-- DROP TABLE achievement;

CREATE TABLE achievement
(
  id serial NOT NULL,
  status hstore,
  user_id integer NOT NULL,
  CONSTRAINT achievement_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE achievement OWNER TO "kakaadmin";


-- 拍卖事件
-- Table: auction_event

-- DROP TABLE auction_event;

CREATE TABLE auction_event
(
  id serial NOT NULL,
  seller integer NOT NULL,
  buyer integer NOT NULL,
  action_time integer NOT NULL,
  CONSTRAINT auction_event_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auction_event OWNER TO "kakaadmin";


-- 收集的图鉴
-- Table: collection

-- DROP TABLE collection;

CREATE TABLE collection
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  status text,
  CONSTRAINT collection_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE collection OWNER TO "kakaadmin";


-- 收集的图鉴组
-- Table: collection_list

-- DROP TABLE collection_list;

CREATE TABLE collection_list
(
  id serial NOT NULL,
  user_id integer,
  status text,
  CONSTRAINT collection_list_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE collection_list OWNER TO kakaadmin;


-- 界面物品摆放信息
-- Table: item

-- DROP TABLE item;

CREATE TABLE item
(
  id serial NOT NULL,
  x integer,
  y integer,
  item_id integer NOT NULL,
  user_id integer NOT NULL,
  created_time integer NOT NULL,
  detail character varying(255),
  CONSTRAINT item_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE item OWNER TO "kakaadmin";

-- 玩家信息
-- Table: player

-- DROP TABLE player;

CREATE TABLE player
(
  id serial NOT NULL,
  sns_id character varying(255),
  gb integer NOT NULL DEFAULT 0,
  kb integer NOT NULL DEFAULT 0,
  energy integer NOT NULL DEFAULT 0,
  vip integer NOT NULL DEFAULT 0,
  regist_time integer DEFAULT 0,
  last_login_time integer,
  last_energy_time integer,
  expand integer DEFAULT 0,
  exp integer DEFAULT 0,
  "level" integer DEFAULT 1,
  title_id integer DEFAULT 0,
  titles character varying(255) DEFAULT 0,
  guide integer DEFAULT 0,
  login_times integer DEFAULT 0,
  free_times integer DEFAULT 0,
  system_reward character varying(255) DEFAULT ''::character varying,
  CONSTRAINT user_pkey PRIMARY KEY (id)
  CONSTRAINT snsid_unique UNIQUE (sns_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE player OWNER TO kakaadmin;


-- 背包信息
-- Table: prop

-- DROP TABLE prop;

CREATE TABLE prop
(
  user_id integer NOT NULL,
  props text,
  capacity integer DEFAULT 120,
  CONSTRAINT prop_pkey PRIMARY KEY (user_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE prop OWNER TO "kakaadmin";


-- 搜索队
-- Table: search_team

-- DROP TABLE search_team;

CREATE TABLE search_team
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  last_start_time integer,
  area integer DEFAULT 1,
  CONSTRAINT search_team_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE search_team OWNER TO "kakaadmin";


-- 前后台会话
-- Table: "session"

-- DROP TABLE "session";

CREATE TABLE "session"
(
  id serial NOT NULL,
  create_time integer NOT NULL,
  skey character varying(100) NOT NULL,
  sns_id character varying(100),
  player_id integer,
  CONSTRAINT id PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "session" OWNER TO kakaadmin;


-- 成就任务(未用到)
-- Table: task

-- DROP TABLE task;

CREATE TABLE task
(
  collection text,
  achievement text,
  user_id integer NOT NULL,
  CONSTRAINT task_pkey PRIMARY KEY (user_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE task OWNER TO "kakaadmin";


-- 拍卖交易记录
-- Table: "transaction"

-- DROP TABLE "transaction";

CREATE TABLE "transaction"
(
  id serial NOT NULL,
  price integer NOT NULL DEFAULT 0,
  "number" integer NOT NULL DEFAULT 0,
  user_id integer NOT NULL,
  prop_id integer NOT NULL DEFAULT 0,
  CONSTRAINT transaction_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "transaction" OWNER TO "kakaadmin";


-- 拍卖日志记录
-- Table: event_log

-- DROP TABLE event_log;

CREATE TABLE event_log
(
  id serial NOT NULL,
  "type" integer NOT NULL,
  user_id integer NOT NULL,
  info text NOT NULL,
  create_time integer,
  CONSTRAINT event_log_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE event_log OWNER TO kakaadmin;


-- 免费礼物
-- Table: free_gift

-- DROP TABLE free_gift;

CREATE TABLE free_gift
(
  id serial NOT NULL,
  sender_id character varying(100) NOT NULL,
  receiver_id character varying(100) NOT NULL,
  op_mode character varying(10),
  gift_id character varying(50) NOT NULL,
  send_time integer,
  verify_code character varying(100),
  is_send_back integer DEFAULT 0,
  is_accept integer DEFAULT 0,
  CONSTRAINT free_gift_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE free_gift OWNER TO kakaadmin;


-- 开箱子信息
-- Table: user_box

-- DROP TABLE user_box;

CREATE TABLE user_box
(
  owner_id character varying(100) NOT NULL,
  helper_ids text,
  is_open integer,
  start_time integer,
  CONSTRAINT user_box_key PRIMARY KEY (owner_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE user_box OWNER TO kakaadmin;


-- 访问好友
-- Table: visit_friend

-- DROP TABLE visit_friend;

CREATE TABLE visit_friend
(
  player_id integer NOT NULL,
  first_visit text,
  daily_visit text,
  visit_time integer,
  CONSTRAINT visit_friend_pkey PRIMARY KEY (player_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE visit_friend OWNER TO kakaadmin;


-- 每日任务
-- Table: daily_task

-- DROP TABLE daily_task;

CREATE TABLE daily_task
(
  player_id integer NOT NULL,
  task_info text,
  task_time integer,
  CONSTRAINT daily_task_pkey PRIMARY KEY (player_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE daily_task OWNER TO kakaadmin;


-- 支付(充值)记录
-- Table: pay

-- DROP TABLE pay;

CREATE TABLE pay
(
  order_id bigint NOT NULL,
  sns_id character varying(100),
  currency character varying(50),
  amount integer,
  pay_time integer,
  kb integer,
  is_done integer DEFAULT 0,
  CONSTRAINT pay_pkey PRIMARY KEY (order_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE pay OWNER TO kakaadmin;


-- 生产材料
-- Table: produce

-- DROP TABLE produce;

CREATE TABLE produce
(
  user_id integer NOT NULL,
  info text,
  CONSTRAINT produce_pkey PRIMARY KEY (user_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE produce OWNER TO kakaadmin;


-- 挖宝验证
-- Table: treasure

-- DROP TABLE treasure;

CREATE TABLE treasure
(
  player_id integer NOT NULL,
  start_time integer DEFAULT 0,
  status integer DEFAULT 0,
  CONSTRAINT treasure_pkey PRIMARY KEY (player_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE treasure OWNER TO kakaadmin;


-- 邀请好友记录
-- Table: invite

-- DROP TABLE invite;

CREATE TABLE invite
(
  invite_id character varying(100) NOT NULL,
  accepter_ids text,
  CONSTRAINT invite_pkey PRIMARY KEY (invite_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE invite OWNER TO kakaadmin;


-- 等级(主线)任务
-- Table: level_task

-- DROP TABLE level_task;

CREATE TABLE level_task
(
  player_id integer NOT NULL,
  task_info text,
  CONSTRAINT level_task_pkey PRIMARY KEY (player_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE level_task OWNER TO kakaadmin;


-- 消费记录
-- Table: cost_log

-- DROP TABLE cost_log;

CREATE TABLE cost_log
(
  id serial NOT NULL,
  player_id integer NOT NULL,
  cost_kb integer,
  cost_action character varying(100),
  cost_time integer,
  CONSTRAINT cost_log_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE cost_log OWNER TO kakaadmin;
