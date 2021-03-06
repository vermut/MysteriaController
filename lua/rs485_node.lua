local machine = require('lua/statemachine')
local rs485 = {}
rs485.__index = rs485

function rs485.create(options)

    local my_node = machine.create(options)

    my_node.slave_id = options.slave_id
    my_node.name = options.name
    my_node.poll_frequency = options.poll_frequency

    REGISTER_MODBUS_SLAVE(my_node)

    -- TODO add callbacks, save triggers etc
    for _, event in ipairs(options.events or {}) do
        if event.action_id then
            my_node["on_" .. event.name] = function()
                MODBUS_ACTION(my_node.slave_id, event.action_id)
            end
        end
    end

    return my_node
end

return rs485